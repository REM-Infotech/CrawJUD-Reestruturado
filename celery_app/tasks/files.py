"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
from celery.app import shared_task
from werkzeug.utils import secure_filename

from addons.storage import Storage

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData

workdir_path = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]


@shared_task(name="upload_files")
async def upload_files(pid: str, files: list[dict[str, str]]) -> None:  # noqa: D103
    storage = Storage("minio")
    upload_folder = workdir_path.joinpath("temp", pid[:6])
    upload_folder.mkdir(parents=True, exist_ok=True)

    for file in files:
        file_name = secure_filename(file)
        file_path = upload_folder.joinpath(file_name)
        await storage.upload_file(f"{pid}/{file_name}", file_path)


@shared_task(name="save_success")
async def save_success(  # noqa: D103
    pid: str,
    data: list[BotData],
    filename: str,
    sheet_name: str = "Resultados",
) -> None:
    storage = Storage("minio")
    path_planilha = workdir_path.joinpath("temp", pid, filename)

    path_planilha.parent.mkdir(exist_ok=True, parents=True)
    df = pd.DataFrame(data)

    with pd.ExcelWriter(path_planilha, engine="openpyxl") as writter:
        df.to_excel(
            excel_writer=writter,
            index=False,
            sheet_name=sheet_name,
        )
    file_name = secure_filename(path_planilha.name)
    await storage.upload_file(f"{pid}/{file_name}", path_planilha)


@shared_task(name="save_success_cache")
async def save_success_cache(  # noqa: D103
    pid: str,
    data: list[BotData],
    filename: str,
    sheet_name: str = "Resultados",
) -> None:
    storage = Storage("minio")
    path_planilha = workdir_path.joinpath("temp", pid, filename)

    path_planilha.parent.mkdir(exist_ok=True, parents=True)
    df = pd.DataFrame(data)

    with pd.ExcelWriter(path_planilha, engine="openpyxl") as writter:
        df.to_excel(
            excel_writer=writter,
            index=False,
            sheet_name=sheet_name,
        )
    file_name = secure_filename(path_planilha.name)
    await storage.upload_file(f"{pid}/{file_name}", path_planilha)
