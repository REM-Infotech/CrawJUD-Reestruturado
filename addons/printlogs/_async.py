"""Módulo de gerenciamento de logs CrawJUD."""

from __future__ import annotations

import asyncio
import traceback
from contextlib import suppress
from datetime import datetime
from os import environ
from typing import Any, Callable, Self

import pytz
from pytz import timezone
from socketio import AsyncClient
from socketio.exceptions import BadNamespaceError

from addons.printlogs._interface import MessageLog
from addons.printlogs._master import PrintLogs


class AsyncPrintMessage(PrintLogs):
    """Classe de gerenciamento de logs CrawJUD."""

    @classmethod
    async def constructor(cls, *args: Any, **kwargs: Any) -> Self:
        self = cls()
        for k, v in list(kwargs.items()):
            setattr(self, k, v)

        self.url_server = environ["SOCKETIO_SERVER_URL"]

        self.io = await self.connect()

        join_data = {"data": {"room": self.pid}}
        await self.io.emit("join_room", data=join_data, namespace=self.namespace)

        self.start_time = datetime.now(pytz.timezone("America/Manaus"))

        return self

    def on(  # noqa: D102
        self,
        event: str,
        namespace: str = None,
    ) -> Callable[..., Any] | None:
        # def set_handler(handler: Callable[..., Any]) -> Callable[..., Any]:
        #     if namespace not in self.handlers:
        #         self.handlers[namespace] = {}
        #     self.handlers[namespace][event] = handler
        #     return handler

        # if handler:
        #     return set_handler
        return self.io.on(event=event, namespace=namespace)

    async def connect(self) -> AsyncClient:  # noqa: D102
        sio = AsyncClient()
        await sio.connect(
            url=self.url_server,
            headers={"Content-Type": "application/json"},
            auth={"room": self.pid},
            namespaces=[self.namespace],
            transports=["websocket"],
            retry=True,
        )
        asyncio.create_task(sio.wait())
        return sio

    async def reconnect(self) -> None:
        """Reestabelece a conexão com o servidor Socket.IO."""
        handlers = self.io.handlers.copy()
        with suppress(Exception):
            self.io.disconnect()
        self.io = self.connect()
        for event, handler in handlers.items():
            self.io.on(event, handler, namespace=self.namespace)

    async def __aenter__(self) -> Self:  # noqa: D105
        return self

    async def __aexit__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, D105
        self.io.disconnect()

    async def emit(  # noqa: D102
        self,
        event: str,
        data: dict[str, str | dict[str, str | MessageLog]],
        callback: Callable[..., Any | None] = None,
    ) -> None:
        try:
            await self.io.emit(event, data, self.namespace, callback=callback)

        except BadNamespaceError:
            with suppress(Exception):
                self.reconnect()
                await self.io.emit(event, data, self.namespace, callback=callback)

    async def print_msg(
        self,
        message: str,
        pid: str = None,
        row: int = 0,
        type_log: str = "log",
        status: str = "Em Execução",
    ) -> None:
        """Print current log message and emit it via the socket.

        Uses internal message attributes, logs the formatted string,
        and appends the output to the messages list.
        """
        time_exec = datetime.now(tz=timezone("America/Manaus")).strftime("%H:%M:%S")
        _pid = self.pid if not pid else pid
        _row = row if row != 0 else self.row
        prompt = f"[({_pid}, {type_log}, {_row}, {time_exec})> {message}]"

        self.total = self.total_rows

        self.logger.info(prompt)
        try:
            total_count = self.total_rows
            remaining = 0
            if _row > 0:
                remaining = total_count + 1 - _row

            time_start = self.start_time.strftime("%d/%m/%Y - %H:%M:%S")
            data = MessageLog(
                message=prompt,
                type=type_log,
                pid=_pid,
                status=status,
                start_time=time_start,
                row=_row,
                total=self.total_rows,
                errors=0,
                success=0,
                remaining=remaining,
            )
            await self.emit("log_execution", data={"data": data})
            self.logger.info(prompt)
        except Exception as e:
            self.logger.error(
                "Erro ao emitir mensagem: Exception %s",
                "\n".join(traceback.format_exception_only(e)),
            )
