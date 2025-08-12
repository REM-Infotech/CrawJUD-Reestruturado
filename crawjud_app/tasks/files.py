"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING, Generic, TypeVar

import pandas as pd
from werkzeug.utils import secure_filename

from crawjud_app._wrapper import shared_task
from crawjud_app.custom._task import ContextTask
from crawjud_app.types import ReturnFormataTempo
from utils.models.logs import CachedExecution
from utils.storage import Storage

if TYPE_CHECKING:
    pass

workdir_path = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]

T = TypeVar("AnyValue", bound=ReturnFormataTempo)


@shared_task(name="save_success", bind=True, base=ContextTask)
class SaveSuccessTask(ContextTask):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        pid: str,
        filename: str,
        *args: Generic[T],
        **kwargs: Generic[T],
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
