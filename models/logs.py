"""
Module for defining the MessageLog model used to store and query log messages in Redis.

Classes:
    MessageLog(HashModel):
        Represents a log entry with details such as process ID, message content, log type, status, timestamps, and processing statistics.

            id_log (int): Unique identifier for the log entry.
            pid (str): Process identifier.
            start_time (str): Timestamp of when the log entry was created.
            row (int): Current row number being processed.
            total (int): Total number of rows to be processed.
            errors (int): Number of errors encountered.
            success (int): Number of successful operations.
            remaining (int): Number of rows remaining to be processed.
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any, Self

from redis_om import Field, JsonModel, NotFoundError

from addons.printlogs._interface import ItemMessageList

description_message = (
    "e.g. '[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]'"
)


class MessageLog(JsonModel):
    """
    Model for message logs.

    Attributes:
        id_log (int): Unique identifier for the log entry (e.g., 1).
        pid (str): Process identifier (e.g., 'C3K7H5').
        message (str): Log message content.
        type (str): Type of log entry (e.g., 'log', 'error', 'success').
        status (str): Status of the process (e.g., 'Em Execução', 'Concluído', 'Erro').
        start_time (str): Timestamp of when the log entry was created (e.g., '01/01/2023 - 19:37:15').
        row (int): Current row number being processed (e.g., 15).
        total (int): Total number of rows to be processed (e.g., 100).
        errors (int): Number of errors encountered (e.g., 2).
        success (int): Number of successful operations (e.g., 98).
        remaining (int): Number of rows remaining to be processed (e.g., 85).

    Methods:
        query_logs(pid: str) -> Self | Type[Self]:
            Retrieves the log entry associated with the given process identifier (pid).

    """

    """Model for message logs."""

    pid: str = Field(
        default="desconhecido",
        description="e.g. 'C3K7H5' (identificador do processo)",
        primary_key=True,
    )

    messages: list[ItemMessageList] = Field(
        default=[ItemMessageList(message="Mensagem não informada")],
        description=description_message,
    )
    type: str = Field(
        default="log", description="e.g. 'log', 'error', 'success' (tipo do log)"
    )
    status: str = Field(
        default="Desconhecido",
        description="e.g. 'Em Execução', 'Concluído', 'Erro' (status do processo)",
    )
    start_time: str = Field(
        default="00/00/0000 - 00:00:00",
        description="e.g. '01/01/2023 - 19:37:15' (data/hora de início)",
    )
    row: int = Field(description="e.g. 15 (linha atual sendo processada)")
    total: int = Field(description="e.g. 100 (total de linhas a serem processadas)")
    errors: int = Field(description="e.g. 2 (quantidade de erros encontrados)")
    success: int = Field(
        description="e.g. 98 (quantidade de operações bem-sucedidas)"
    )
    remaining: int = Field(description="e.g. 85 (linhas restantes para processar)")

    @classmethod
    def query_logs(cls, pid: str) -> Self:  # noqa: D102
        with suppress(NotFoundError, Exception):
            log_pks = cls.all_pks()

            for pk in log_pks:
                if pk == pid:
                    return cls.get(pk)


class CachedExecution(JsonModel):  # noqa: D101
    processo: str = Field(description="Processo Juridico", primary_key=True)
    pid: str = Field(
        default="desconhecido",
        description="e.g. 'C3K7H5' (identificador do processo)",
    )
    data: list[dict[str, Any]] = Field()
