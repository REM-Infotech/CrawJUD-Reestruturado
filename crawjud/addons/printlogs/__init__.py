"""Módulo de gerenciamento de logs CrawJUD."""

import asyncio
import logging
import traceback
from datetime import datetime
from os import environ
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
        asyncio.run(self.emit_message)

    async def emit_message(self) -> None:
        """Envia a mensagem para o servidor SocketIO."""
        try:
            async with socketio.AsyncSimpleClient() as sio:
                await sio.connect(
                    url=self.url_server,
                    headers={"Content-Type": "application/json"},
                    namespace=self.namespace,
                    transports="websocket",
                )

                await sio.emit(
                    "log_bot",
                    data={
                        "message": self.message,
                        "pid": self.pid,
                        "type": self.type_log,
                        "pos": self.row,
                        "total": self.total_rows,
                    },
                )

        except Exception as e:
            self.logger.error("Erro ao emitir mensagem: Exception %s", "\n".join(traceback.format_exception_only(e)))
