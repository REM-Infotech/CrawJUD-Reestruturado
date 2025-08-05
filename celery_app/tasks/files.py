"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pandas as pd
from werkzeug.utils import secure_filename

from celery_app._wrapper import shared_task
from models.logs import CachedExecution
from utils.storage import Storage

if TYPE_CHECKING:
    from crawjud.types import BotData

workdir_path = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]


@shared_task(name="save_success")
async def save_success(  # noqa: D103
    pid: str, filename: str
) -> None:
    _data_query = CachedExecution.find(CachedExecution.pid == pid).all()

    list_data = []
    for item in _data_query:
        list_data.extend(item.data)

    storage = Storage("minio")
    path_planilha = workdir_path.joinpath("temp", pid, filename)

    path_planilha.parent.mkdir(exist_ok=True, parents=True)
    df = pd.DataFrame(list_data)

    with pd.ExcelWriter(path_planilha, engine="openpyxl") as writter:
        df.to_excel(excel_writer=writter, index=False, sheet_name="Resultados")

    file_name = secure_filename(path_planilha.name)
    storage.upload_file(f"{pid}/{file_name}", path_planilha)


@shared_task(name="save_cache")
async def save_success_cache(  # noqa: D103
    pid: str,
    data: list[BotData],
    processo: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    _cache = CachedExecution(processo=processo, data=data, pid=pid)
    _cache.save()
