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

from contextlib import suppress
from typing import Self, Type

from redis_om import Field, HashModel, NotFoundError

description_message = (
    "e.g. '[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]'"
)


class MessageLog(HashModel):
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

    id_log: int = Field(
        description="e.g. 1 (unique identifier for the log entry)", sortable=True
    )
    pid: str = Field(description="e.g. 'C3K7H5'")
    message: str = Field(description=description_message)
    type: str = Field(description="e.g. 'log', 'error', 'success'")
    status: str = Field(description="e.g. 'Em Execução', 'Concluído', 'Erro'")
    start_time: str = Field(description="e.g. '01/01/2023 - 19:37:15'")
    row: int = Field(description="e.g. 15 (current row number)")
    total: int = Field(description="e.g. 100 (total rows processed)")
    errors: int = Field(description="e.g. 2 (number of errors encountered)")
    success: int = Field(description="e.g. 98 (number of successful operations)")
    remaining: int = Field(description="e.g. 85 (rows remaining to be processed)")

    @classmethod
    def query_logs(cls, pid: str) -> Self | Type[Self]:  # noqa: D102
        with suppress(NotFoundError, Exception):
            log = cls.get(pid)
            return log
