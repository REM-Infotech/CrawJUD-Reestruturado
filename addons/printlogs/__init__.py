"""Módulo de gerenciamento de logs CrawJUD."""

import logging
import traceback
from datetime import datetime
from os import environ
from time import sleep
from typing import Any, Callable, Self

from pytz import timezone
from socketio import Client


class PrintMessage:
    """Classe de gerenciamento de logs CrawJUD."""

    url_server: str
    namespace: str
    row: int
    pid: str
    message: str
    _total_rows: int
    _logger: logging.Logger
    _io: Client

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

    def __init__(self, *args: Any, **kwrgs: Any) -> None:
        """Inicializa o PrintMessage."""
        for k, v in list(kwrgs.items()):
            setattr(self, k, v)

        self.url_server = environ["SOCKETIO_SERVER_URL"]
        self.namespace = environ["SOCKETIO_SERVER_NAMESPACE"]

        sio = Client()
        sio.connect(
            url=self.url_server,
            headers={"Content-Type": "application/json"},
            auth={"room": self.pid},
            namespaces=[self.namespace],
            transports=["websocket"],
            retry=True,
        )

        self.io = sio

    def __enter__(self) -> Self:  # noqa: D105
        return self

    def __exit__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, D105
        self.io.disconnect()

    @property
    def logger(self) -> logging.Logger:  # noqa: D102
        return self._logger

    @logger.setter
    def logger(self, new_logger: logging.Logger) -> None:
        self._logger = new_logger

    @property
    def io(self) -> Client:  # noqa: D102
        return self._io

    @io.setter
    def io(self, new_socket: Client) -> None:
        self._io = new_socket

    @property
    def total_rows(self) -> int:  # noqa: D102
        return self._total_rows

    @total_rows.setter
    def total_rows(self, new_value: int) -> None:
        self._total_rows = new_value

    def print_msg(
        self,
        message: str,
        pid: str,
        row: int,
        type_log: str = "log",
    ) -> None:
        """Print current log message and emit it via the socket.

        Uses internal message attributes, logs the formatted string,
        and appends the output to the messages list.
        """
        time_exec = datetime.now(tz=timezone("America/Manaus")).strftime("%H:%M:%S")
        prompt = f"[({pid}, {type_log}, {row}, {time_exec})> {message}]"

        self.type_log = type_log
        self.row = row
        self.total = self.total_rows
        self.pid = pid
        self.message = prompt

        self.logger.info(prompt)
        try:
            self.io.emit("join_room", data={"room": self.pid})
            sleep(1)
            self.io.emit(
                "log_execution",
                data={
                    "message": self.message,
                    "pid": self.pid,
                    "type": self.type_log,
                    "pos": self.row,
                    "total": self.total_rows,
                },
                namespace=self.namespace,
            )
            sleep(1)

        except Exception as e:
            self.logger.error(
                "Erro ao emitir mensagem: Exception %s",
                "\n".join(traceback.format_exception_only(e)),
            )
