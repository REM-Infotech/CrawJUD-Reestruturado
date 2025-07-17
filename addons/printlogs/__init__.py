"""Módulo de gerenciamento de logs CrawJUD."""

from __future__ import annotations

import logging
import traceback
from contextlib import suppress
from datetime import datetime
from os import environ
from time import sleep
from typing import TYPE_CHECKING, Any, Callable, Self, TypedDict

import pytz
from pytz import timezone
from socketio import Client
from socketio.exceptions import BadNamespaceError

if TYPE_CHECKING:
    from common.bot import ClassBot

_namespace = environ["SOCKETIO_SERVER_NAMESPACE"]

sio = Client()


class PrintLogs:  # noqa: D101
    namespace: str = _namespace
    url_server: str
    row: int
    pid: str
    message: str
    _logger: logging.Logger = logging.getLogger(__name__)
    _total_rows: int = 0
    _start_time: datetime
    _bot_instance: ClassBot = None

    @property
    def io(self) -> Client:  # noqa: D102
        return sio

    @property
    def bot_instance(self) -> ClassBot:  # noqa: D102
        return self._bot_instance

    @bot_instance.setter
    def bot_instance(self, inst: ClassBot) -> None:
        self._bot_instance = inst

    @property
    def start_time(self) -> datetime:  # noqa: D102
        return self._start_time

    @start_time.setter
    def start_time(self, time_set: datetime) -> None:
        self._start_time = time_set

    @property
    def logger(self) -> logging.Logger:  # noqa: D102
        return self._logger

    @logger.setter
    def logger(self, new_logger: logging.Logger) -> None:
        self._logger = new_logger

    @property
    def total_rows(self) -> int:  # noqa: D102
        return self._total_rows

    @total_rows.setter
    def total_rows(self, new_value: int) -> None:
        self._total_rows = new_value

    @property
    def row(self) -> int:  # noqa: D102
        return self._bot_instance.row if self._bot_instance else 0


class MessageLog(TypedDict):  # noqa: D101
    message: str
    type: str
    pid: str
    status: str
    start_time: str

    # counts
    row: int
    total: int
    errors: int
    success: int
    remaining: int


class PrintMessage(PrintLogs):
    """Classe de gerenciamento de logs CrawJUD."""

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

    def connect(self) -> Client:  # noqa: D102
        sio.connect(
            url=self.url_server,
            headers={"Content-Type": "application/json"},
            auth={"room": self.pid},
            namespaces=[self.namespace],
            transports=["websocket"],
            retry=True,
        )

        return sio

    def __init__(self, *args: Any, **kwrgs: Any) -> None:
        """Inicializa o PrintMessage."""
        for k, v in list(kwrgs.items()):
            setattr(self, k, v)

        self.url_server = environ["SOCKETIO_SERVER_URL"]

        self.connect()

        join_data = {"data": {"room": self.pid}}
        sio.emit("join_room", data=join_data, namespace=self.namespace)

        self.start_time = datetime.now(pytz.timezone("America/Manaus"))

    def __enter__(self) -> Self:  # noqa: D105
        return self

    def __exit__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, D105
        self.io.disconnect()

    def emit(  # noqa: D102
        self,
        event: str,
        data: dict[str, str | dict[str, str | MessageLog]],
        callback: Callable[..., Any | None] = None,
    ) -> None:
        try:
            self.io.emit(event, data, self.namespace, callback=callback)

        except BadNamespaceError:
            with suppress(Exception):
                self.connect()
                self.io.emit(event, data, self.namespace, callback=callback)

    def print_msg(
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
        prompt = f"[({_pid}, {type_log}, {self.row}, {time_exec})> {message}]"

        self.total = self.total_rows

        self.logger.info(prompt)
        try:
            sleep(1)

            total_count = self.total_rows
            remaining = total_count + 1 - self.row
            time_start = self.start_time.strftime("%d/%m/%Y - %H:%M:%S")
            data = MessageLog(
                message=prompt,
                type=type_log,
                pid=_pid,
                status=status,
                start_time=time_start,
                row=self.row,
                total=self.total_rows,
                errors=0,
                success=0,
                remaining=remaining,
            )
            self.emit("log_execution", data={"data": data})
            sleep(1)

        except Exception as e:
            self.logger.error(
                "Erro ao emitir mensagem: Exception %s",
                "\n".join(traceback.format_exception_only(e)),
            )
