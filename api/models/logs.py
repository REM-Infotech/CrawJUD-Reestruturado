"""MessageLog model for logging messages in the application."""

from pydantic import PositiveInt
from redis_om import Field, HashModel

description_message = (
    "e.g. '[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]'"
)

posInt = PositiveInt  # noqa: N816


class MessageLog(HashModel):
    """Model for message logs."""

    pid: str = Field(description="e.g. 'C3K7H5'", primary_key=True)
    message: str = Field(description=description_message)
    type: str = Field(description="e.g. 'log', 'error', 'success'")
    status: str = Field(description="e.g. 'Em Execução', 'Concluído', 'Erro'")
    start_time: str = Field(description="e.g. '01/01/2023 - 19:37:15'")
    row: posInt = Field(description="e.g. 15 (current row number)", sortable=True)
    total: posInt = Field(description="e.g. 100 (total rows processed)")
    errors: posInt = Field(description="e.g. 2 (number of errors encountered)")
    success: posInt = Field(description="e.g. 98 (number of successful operations)")
    remaining: posInt = Field(description="e.g. 85 (rows remaining to be processed)")
