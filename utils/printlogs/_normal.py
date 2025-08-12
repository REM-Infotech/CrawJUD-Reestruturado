"""Módulo de gerenciamento de logs CrawJUD."""

from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from os import environ
from typing import TYPE_CHECKING, Any, Self
from zoneinfo import ZoneInfo

from socketio import Client
from socketio.exceptions import BadNamespaceError

from utils.printlogs._interface import MessageLog
from utils.printlogs._master import PrintLogs

if TYPE_CHECKING:
    from collections.abc import Callable


class PrintMessage[T](PrintLogs):
    """Classe de gerenciamento de logs CrawJUD."""

    @property
    def io(self) -> Client:
        return self._sio

    @io.setter
    def io(self, new_io: Client) -> None:
        self._sio = new_io

    def on(
        self,
        event: str,
        namespace: str | None = None,
    ) -> Callable[..., Any] | None:
        return self.io.on(event=event, namespace=namespace)

    def connect(self) -> Client:
        sio = Client()
        sio.connect(
            url=self.url_server,
            headers={"Content-Type": "application/json"},
            auth={"room": self.pid},
            namespaces=[self.namespace],
            transports=["websocket"],
            retry=True,
        )

        return sio

    def reconnect(self) -> None:
        """Reestabelece a conexão com o servidor Socket.IO."""
        handlers = self.io.handlers.copy()
        with suppress(Exception):
            self.io.disconnect()
        self.io = self.connect()
        for event, handler in handlers.items():
            self.io.on(event, handler, namespace=self.namespace)

    def __init__(self, *args: T, **kwrgs: T) -> None:
        """Inicializa o PrintMessage."""
        for k, v in kwrgs.items():
            setattr(self, k, v)

        self.url_server = environ["SOCKETIO_SERVER_URL"]

        self.io = self.connect()

        join_data = {"data": {"room": self.pid}}
        self.io.emit("join_room", data=join_data, namespace=self.namespace)

        self.start_time = datetime.now(ZoneInfo("America/Manaus"))

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        self.io.disconnect()

    def emit(
        self,
        event: str,
        data: dict[str, str | dict[str, str | MessageLog]],
        callback: Callable[..., Any | None] | None = None,
    ) -> None:
        try:
            self.io.emit(event, data, self.namespace, callback=callback)

        except BadNamespaceError:
            with suppress(Exception):
                self.reconnect()
                self.io.emit(event, data, self.namespace, callback=callback)

    def print_msg(
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

        self.total = self.total_rows

        self.logger.info(prompt)
        try:
            total_count = self.total_rows
            remaining = 0
            if row_ > 0:
                remaining = total_count + 1 - row_

            time_start = self.start_time.strftime("%d/%m/%Y - %H:%M:%S")
            data = MessageLog(
                message=prompt,
                type=type_log,
                pid=pid_,
                status=status,
                start_time=time_start,
                row=row_,
                total=self.total_rows,
                errors=0,
                success=0,
                remaining=remaining,
            )
            self.emit("log_execution", data={"data": data})
            self.logger.info(prompt)
        except Exception:
            self.logger.exception(
                "Erro ao emitir mensagem.",
            )
