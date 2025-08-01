# noqa: D104
from typing import TypedDict


class ItemMessageList(TypedDict):
    """
    TypedDict representing a log message item.

    Attributes:
        id_log (int | None): Unique identifier for the log entry. Example: 1.
        message (str | None): The log message content. Example: "[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]"

    """

    id_log: int | None  # e.g. 1 (unique identifier for the log entry)
    message: (
        str
        | None  # e.g. "[(C3K7H5, log, 15, 19:37:15)> Salvando arquivos na pasta...]"
    )
