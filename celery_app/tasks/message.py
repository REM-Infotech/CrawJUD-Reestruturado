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
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from dotenv import dotenv_values
from pytz import timezone
from socketio import AsyncSimpleClient

from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from utils.models.logs import MessageLogDict

if TYPE_CHECKING:
    pass


environ = dotenv_values()
workdir_path = Path(__file__).cwd()
T = TypeVar("T")
server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]


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


@shared_task(name="print_message")
async def print_message(
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
    with suppress(Exception):
        # Cria uma instância do cliente Socket.IO e conecta ao servidor
        # com o namespace e cabeçalhos especificados.
        # Se uma sala for especificada, o cliente se juntará a ela.
        # Em seguida, emite o evento com os dados fornecidos.
        async with AsyncSimpleClient(
            reconnection_attempts=20,
            reconnection_delay=5,
        ) as sio:
            # Conecta ao servidor Socket.IO com o URL, namespace e cabeçalhos especificados.

            await sio.connect(
                url=server,
                namespace=namespace,
                headers=headers,
                transports=transports,
            )

            # Se uma sala for especificada, o cliente se juntará a ela.
            if room:
                join_data = {"data": {"room": room}}
                await sio.emit("join_room", data=join_data)

            # Emite o evento com os dados fornecidos.
            await sio.emit(event, data={"data": data})


@shared_task(name="log_message")
def log_message(  # noqa: D417
    pid: str,
    message: str,
    row: int,
    type_log: str = "log",
    status: str = "Em Execução",
    total_rows: int = 0,
    start_time: StrTime = None,
    *args: Generic[T],
    **kwargs: Generic[T],
) -> None:
    """
    Formata e envia mensagem de log para o sistema de monitoramento via Socket.IO.

    Args:
        pid (str): Identificador do processo.
        message (str): Mensagem a ser registrada.
        row (int): Linha ou índice relacionado à execução.
        type_log (str): Tipo do log (padrão: "log").
        status (str): Status da execução (padrão: "Em Execução").
        total_rows (int): Total de linhas ou itens processados (padrão: 0).
        start_time (StrTime): Momento de início da execução.

    Returns:
        None: Não retorna valor.

    """
    # Mantém o pid para referência
    pid = pid
    # Cria subtask para envio da mensagem
    task_msg = subtask("print_message")
    # Define o total de itens
    total_count = total_rows
    # Obtém o horário atual formatado
    time_exec = datetime.now(tz=timezone("America/Manaus")).strftime("%H:%M:%S")
    # Monta o prompt da mensagem
    prompt = f"[({pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"

    # Cria objeto de log da mensagem
    data = MessageLogDict(
        message=prompt,
        pid=str(pid),
        row=row,
        type=type_log,
        status=status,
        total=total_count,
        success=0,
        errors=0,
        remaining=total_rows,
        start_time=start_time,
    )

    # Envia a mensagem formatada para o sistema de monitoramento
    task_msg.apply_async(
        kwargs={
            "event": "log_execution",
            "data": data,
            "room": str(pid),
        }
    )
