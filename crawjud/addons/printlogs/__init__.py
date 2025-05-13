"""Módulo de gerenciamento de logs CrawJUD."""

import logging
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

        self.logger.info(prompt)

    async def emit_message(self) -> None:
        """Envia a mensagem para o servidor SocketIO."""
        async with socketio.AsyncSimpleClient() as sio:
            await sio.connect(
                url=self.url_server, headers={"Content-Type": "application/json"}, namespace=self.namespace
            )
