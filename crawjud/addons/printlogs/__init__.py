"""Módulo de gerenciamento de logs CrawJUD."""

import logging
import traceback
from datetime import datetime
from os import environ
from time import sleep
from typing import Self

import socketio
from pytz import timezone


class PrintMessage:
    """Classe de gerenciamento de logs CrawJUD."""

    logger: logging.Logger
    url_server: str
    namespace: str
    total_rows: int
    row: int
    pid: str
    message: str

    def __init__(self, **kwrgs: str | object) -> None:
        """Inicializa o PrintMessage."""
        for k, v in list(kwrgs.items()):
            setattr(self, k, v)

        self.url_server = environ["SOCKETIO_SERVER_URL"]
        self.namespace = environ["SOCKETIO_SERVER_NAMESPACE"]

    @classmethod
    def constructor(cls, **kwrgs: str | object) -> Self:
        """Construtor do PrintMessage.

        Arguments:
            **kwrgs (str|object): Argumentos de inicialização
                * logger (logging.Logger): logger da aplicação.

        """
        return cls(**kwrgs)

    def print_msg(self, message: str, pid: str, row: int, type_log: str = "log") -> None:
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
        self.emit_message()

    def emit_message(self) -> None:
        """Envia a mensagem para o servidor SocketIO."""
        try:
            with socketio.SimpleClient() as sio:
                sio.connect(
                    url=self.url_server,
                    headers={"Content-Type": "application/json"},
                    namespace=self.namespace,
                    transports=["websocket"],
                )

                sio.emit(
                    "log_execution",
                    data={
                        "message": self.message,
                        "pid": self.pid,
                        "type": self.type_log,
                        "pos": self.row,
                        "total": self.total_rows,
                    },
                )
                sleep(1)

        except Exception as e:
            self.logger.error("Erro ao emitir mensagem: Exception %s", "\n".join(traceback.format_exception_only(e)))
