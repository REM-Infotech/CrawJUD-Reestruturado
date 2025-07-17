from typing import TypedDict


class MessageLog(TypedDict):  # noqa: D101
    message: (
        str  # e.g. "[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]"
    )
    type: str  # e.g. "log", "error", "success"
    pid: str  # e.g. "C3K7H5"
    status: str  # e.g. "Em Execução", "Concluído", "Erro"
    start_time: str  # e.g. "01/01/2023 - 19:37:15"

    # counts
    row: int  # e.g. 15 (current row number)
    total: int  # e.g. 100 (total rows processed)
    errors: int  # e.g. 2 (number of errors encountered)
    success: int  # e.g. 98 (number of successful operations)
    remaining: int  # e.g. 85 (rows remaining to be processed)
