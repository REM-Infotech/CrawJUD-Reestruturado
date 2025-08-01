# noqa: D104
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic

from celery import chain  # noqa: F401
from dotenv import load_dotenv

from celery_app._wrapper import classmethod_shared_task, shared_task
from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask
from celery_app.types._celery._canvas import AsyncResult
from celery_app.types._celery._task import Task as Task
from common.bot import ClassBot
from crawjud._wrapper import wrap_init
from crawjud.exceptions.bot import ExecutionError
from crawjud.types.bot import (
    DictFiles,
    DictReturnAuth,
    TReturnAuth,
)
from crawjud.types.bot import (
    MessageTimeoutAutenticacao as MessageTimeoutAutenticacao,
)
from crawjud.types.pje import DictSeparaRegiao

if TYPE_CHECKING:
    from crawjud.types import BotData, T  # noqa: F401

load_dotenv()


@wrap_init
class Capa(ClassBot):  # noqa: D101
    @staticmethod
    @shared_task(name="pje.movimentacao")
    def pje_capa(  # noqa: D102
        current_task: ContextTask,
        name: str,
        system: str,
        storage_folder_name: str,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        _pid = str(current_task.request.id)
        _keyword_args = kwargs.copy()

        _task_download_files = subtask("crawjud.download_files")
        _task_autenticacao = subtask("pje.autenticador")
        _task_bot_data = subtask("crawjud.dataFrame")
        _task_separa_regiao = subtask("pje.separar_regiao")

        _files_b64: list[DictFiles] = _task_download_files.apply_async(
            kwargs={"storage_folder_name": storage_folder_name}
        ).wait_ready()

        xlsx_key = list(filter(lambda x: x["file_suffix"] == ".xlsx", _files_b64))
        if not xlsx_key:
            raise ExecutionError(
                bot_execution_id=_pid, message="Nenhum arquivo Excel encontrado."
            )

        _bot_data: list[BotData] = _task_bot_data.apply_async(
            kwargs={"base91_planilha": xlsx_key[0]["file_base91str"]}
        ).wait_ready()

        regioes: DictSeparaRegiao = _task_separa_regiao.apply_async(
            kwargs={"frame": _bot_data}
        ).wait_ready()

        _position_process = regioes["position_process"]
        regiao_session: dict[str, DictReturnAuth] = {}
        _tasks_auth: list[AsyncResult] = []
        for regiao, _ in list(regioes["regioes"].items()):
            autenticacao_data: TReturnAuth = _task_autenticacao.apply_async(
                kwargs={"regiao": regiao}
            ).wait_ready()
            if isinstance(autenticacao_data, dict):
                regiao_session[regiao] = autenticacao_data

        print("ok")

    @classmethod
    @classmethod_shared_task(name="pje.tratamento_dados")
    def tratamento_dados(cls, *args: Any, **kwargs: Any) -> None:  # noqa: D102, N805
        print("teste!")
