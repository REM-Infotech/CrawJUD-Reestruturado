"""
Defines Celery tasks for initializing and executing bot instances dynamically.

Tasks:
    - initialize_bot: Asynchronously initializes and executes a bot instance based on the provided name, system, and process ID (pid). Handles dynamic import of the bot module and class, downloads required files from storage, sets up logging, and manages stop signals via Socket.IO.
    - scheduled_initialize_bot: Synchronously initializes and executes a bot instance for scheduled tasks, using the provided bot name, system, and configuration path.

Dependencies:
    - Dynamic import of bot modules and classes.
    - Storage management for downloading required files.
    - PrintMessage for logging and communication.
    - Socket.IO for handling stop signals during bot execution.

Raises:
    - ImportError: If the specified bot class cannot be found in the dynamically imported module.
    - Exception: Catches and logs any exceptions during bot initialization or execution.

"""

from __future__ import annotations

import re
from contextlib import suppress
from pathlib import Path
from threading import Thread
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from dotenv import dotenv_values

from celery_app import sio
from celery_app._wrapper import shared_task
from celery_app.custom._task import ContextTask

if TYPE_CHECKING:
    pass


environ = dotenv_values()
workdir_path = Path(__file__).cwd()
T = TypeVar("T")


server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


class StrTime(str):
    """
    Representa uma string de data/hora com validação de formatos específicos.

    Esta classe permite verificar se uma instância corresponde a padrões de data/hora
    definidos por expressões regulares.

    Args:
        instance (Any): Instância a ser verificada.

    Returns:
        bool: Indica se a instância corresponde a algum dos padrões de data/hora.

    """

    __slots__ = ()

    def __str__(self) -> str:  # noqa: D105
        return self

    def __repr__(self) -> str:  # noqa: D105
        return self

    def __instancecheck__(self, instance: Any) -> bool:  # noqa: D105
        # Lista de padrões para validação de datas/horas
        pattern_list = [
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}Z$",
            r"^\d{4}-\d{2}-\d{2}"
            r"^\d{2}:\d{2}:\d{2}$",
            r"^\d{4}-\d{2}-\d{2}.\d{1,6}$",
        ]

        if any(re.match(pattern, instance) for pattern in pattern_list):
            return True

        return False


@shared_task(name="print_message", bind=True, base=ContextTask)
class PrintMessage(ContextTask):
    """
    Classe responsável por enviar mensagens de log para o sistema de monitoramento.

    Esta classe utiliza o Socket.IO para enviar mensagens de log assíncronas, permitindo
    a comunicação em tempo real com o sistema de monitoramento.
    """

    def __init__(  # noqa: D107
        self,
        event: str = "log_execution",
        data: dict[str, str] | str = None,
        room: str = None,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        self.print_msg(event=event, data=data, room=room, *args, **kwargs)  # noqa: B026

    def print_msg(
        self,
        event: str = "log_execution",
        data: dict[str, str] | str = None,
        room: str = None,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        """
        Envia mensagem assíncrona para o sistema de monitoramento via Socket.IO.

        Args:
            event (str): Evento a ser emitido (padrão: "log_execution").
            data (dict[str, str] | str): Dados da mensagem a ser enviada.
            room (str): Sala para envio da mensagem (opcional).
            *args: Argumentos posicionais adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            None: Não retorna valor.

        """
        if data:
            with suppress(Exception):
                sio.connect(
                    url=server,
                    namespaces=["/logsbot", "/bots"],
                    headers=headers,
                    transports=transports,
                )
                # Cria uma instância do cliente Socket.IO e conecta ao servidor
                # com o namespace e cabeçalhos especificados.
                # Se uma sala for especificada, o cliente se juntará a ela.
                # Em seguida, emite o evento com os dados fornecidos.

                # Se uma sala for especificada, o cliente se juntará a ela.
                if room:
                    join_data = {"data": {"room": room}}
                    sio.emit("join_room", data=join_data, namespace="/logsbot")

                # Emite o evento com os dados fornecidos.
                sio.emit("log_execution", data={"data": data}, namespace="/logsbot")

                wait_server = Thread(target=sio.wait, daemon=True)

                wait_server.start()

                wait_server.join(30)
