# noqa: D100
from datetime import datetime
from typing import TypedDict

from werkzeug.datastructures import FileMultiDict


class JuridicoFormFileAuth(TypedDict):  # noqa: D101
    xlsx: FileMultiDict
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormMultipleFiles(TypedDict):  # noqa: D101
    xlsx: FileMultiDict
    otherfiles: list[FileMultiDict]
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormOnlyAuth(TypedDict):  # noqa: D101
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormOnlyFile(TypedDict):  # noqa: D101
    xlsx: FileMultiDict
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormPautas(TypedDict):  # noqa: D101
    varas: list[str]
    data_inicio: str | datetime
    data_fim: str | datetime
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None


class JuridicoFormProcParte(TypedDict):  # noqa: D101
    parte_name: str
    doc_parte: str
    polo_parte: str
    varas: list[str]
    data_inicio: str | datetime
    data_fim: str | datetime
    varas: list[str]
    creds: str
    state: str
    confirm_fields: bool
    periodic_task: bool
    task_name: str | None
    task_hour_minute: str | None
    email_notify: str | None
    days_task: list | None
