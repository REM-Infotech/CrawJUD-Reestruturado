"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from os import environ
from pathlib import Path

import pandas as pd
from werkzeug.utils import secure_filename

from crawjud_app.custom.task import ContextTask
from crawjud_app.decorators import shared_task
from utils.models.logs import CachedExecution
from utils.storage import Storage

workdir_path = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]


@shared_task(name="save_success", bind=True, base=ContextTask)
class SaveSuccessTask(ContextTask):
    """Gerencia a tarefa de salvar resultados em Excel e realizar upload.

    Args:
        pid (str): Identificador do processo de execução.
        filename (str): Nome do arquivo a ser salvo.

    Returns:
        None: Não retorna valor.

    Raises:
        FileNotFoundError: Caso o diretório de destino não exista.

    """

    def __init__(
        self,
        pid: str,
        filename: str,
    ) -> None:
        """Inicializa a tarefa SaveSuccessTask com o PID e nome do arquivo.

        Args:
            pid (str): Identificador do processo de execução.
            filename (str): Nome do arquivo a ser salvo.

        """
        data_query_ = CachedExecution.find(CachedExecution.pid == pid).all()

        list_data = []
        for item in data_query_:
            list_data.extend(item.data)

        storage = Storage("minio")
        path_planilha = workdir_path.joinpath("temp", pid, filename)

        path_planilha.parent.mkdir(exist_ok=True, parents=True)
        df = pd.DataFrame(list_data)

        with pd.ExcelWriter(path_planilha, engine="openpyxl") as writter:
            df.to_excel(excel_writer=writter, index=False, sheet_name="Resultados")

        file_name = secure_filename(path_planilha.name)
        storage.upload_file(f"{pid}/{file_name}", path_planilha)
