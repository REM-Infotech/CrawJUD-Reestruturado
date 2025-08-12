"""Módulo de gerenciamento de logs CrawJUD."""

from __future__ import annotations

import asyncio
from contextlib import suppress
from datetime import datetime
from os import environ
from typing import TYPE_CHECKING, Any, ClassVar, Self
from zoneinfo import ZoneInfo

from socketio import AsyncClient
from socketio.exceptions import BadNamespaceError

from crawjud_app import app
from utils.printlogs._interface import MessageLog
from utils.printlogs._master import PrintLogs

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


class AsyncPrintMessage[T](PrintLogs):
    """Classe de gerenciamento de logs CrawJUD."""

    transports: ClassVar[list[str]] = ["websocket"]
    headers: ClassVar[dict[str, str]] = {"Content-Type": "application/json"}
    url_server: ClassVar[str] = environ["SOCKETIO_SERVER_URL"]

    @property
    def io(self) -> AsyncClient:
        return self._sio

    @classmethod
    async def constructor(cls, kwargs: Mapping[str, T]) -> Self:
        self = cls()
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.io = await self.connect()
        for k, v in kwargs.items():
            setattr(self, k, v)

        self.io = await self.connect()

        join_data = {"data": {"room": self.pid}}
        await self.io.emit("join_room", data=join_data, namespace=self.namespace)

        self.start_time = datetime.now(ZoneInfo("America/Manaus"))

        return self

    def on(
        self,
        event: str,
        namespace: str | None = None,
    ) -> Callable[..., Any] | None:
        return self.io.on(event=event, namespace=namespace)

    async def connect(self) -> AsyncClient:
        sio = AsyncClient(reconnection_attempts=20, reconnection_delay=5)
        await sio.connect(
            url=self.url_server,
            headers=self.headers,
            namespaces=[self.namespace],
            transports=self.transports,
            retry=True,
        )
        return sio

    async def reconnect(self) -> None:
        """Reestabelece a conexão com o servidor Socket.IO."""
        handlers = self.io.handlers.copy()
        with suppress(Exception):
            self.io.disconnect()
        self.io = self.connect()
        for event, handler in handlers.items():
            self.io.on(event, handler, namespace=self.namespace)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        self.io.disconnect()

    async def emit(
        self,
        event: str,
        data: dict[str, str | dict[str, str | MessageLog]],
        callback: Callable[..., Any | None] | None = None,
    ) -> None:
        # Armazena tarefas para evitar coleta prematura de lixo
        if not hasattr(self, "_background_tasks"):
            self._background_tasks = set()

        try:
            task = asyncio.create_task(
                self.io.emit(event, data, self.namespace, callback=callback),
            )
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        except BadNamespaceError:
            with suppress(Exception):
                self.reconnect()
                task = asyncio.create_task(
                    self.io.emit(event, data, self.namespace, callback=callback),
                )
                self._background_tasks.add(task)
                task.add_done_callback(self._background_tasks.discard)

    async def print_msg(
        self,
        message: str,
        pid: str | None = None,
        row: int = 0,
        type_log: str = "log",
        status: str = "Em Execução",
    ) -> None:
        """Print current log message and emit it via the socket.

        Uses internal message attributes, logs the formatted string,
        and appends the output to the messages list.
        """
        time_exec = datetime.now(tz=ZoneInfo("America/Manaus")).strftime("%H:%M:%S")
        pid_ = pid or self.pid
        row_ = row if row != 0 else self.row
        prompt = f"[({pid_}, {type_log}, {row_}, {time_exec})> {message}]"

        data = await self.message_format(pid_, row_, prompt, type_log, status)
        self.total = self.total_rows
        self.logger.info(prompt)

        app.send_task(
            "crawjud_app.tasks.bot.print_message",
            kwargs={
                "data": data,
                "server": self.url_server,
                "namespace": self.namespace,
                "headers": self.headers,
                "transports": self.transports,
            },
        )

        try:
            self.logger.info(prompt)
        except Exception:
            self.logger.exception(
                "Erro ao emitir mensagem",
            )

    async def message_format(
        self,
        pid: str | None = None,
        row: int = 0,
        prompt: str | None = None,
        type_log: str | None = None,
        status: str | None = None,
    ) -> MessageLog:
        total_count = self.total_rows
        remaining = 0
        if row > 0:
            remaining = total_count + 1 - row

        time_start = self.start_time.strftime("%d/%m/%Y - %H:%M:%S")
        return MessageLog(
            message=prompt,
            type=type_log,
            pid=pid,
            status=status,
            start_time=time_start,
            row=row,
            total=self.total_rows,
            errors=0,
            success=0,
            remaining=remaining,
        )
