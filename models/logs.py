"""MessageLog model for logging messages in the application."""

from contextlib import suppress
from typing import Self, Type

from redis_om import Field, HashModel, NotFoundError

description_message = (
    "e.g. '[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]'"
)


class MessageLog(HashModel):
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
