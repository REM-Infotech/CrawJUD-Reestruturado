# noqa: D104
from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING, Generic

import psutil
from celery import chain  # noqa: F401
from dotenv import load_dotenv

from celery_app._wrapper import classmethod_shared_task as classmethod_shared_task
from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask
from celery_app.types._celery._canvas import AsyncResult
from celery_app.types._celery._task import Task as Task
from common.bot import ClassBot
from crawjud._wrapper import wrap_init
from crawjud.bots.resources.formatadores import formata_tempo
from crawjud.exceptions.bot import ExecutionError
from crawjud.types.bot import (
    DictFiles,
    DictReturnAuth,
    TReturnAuth,
)
from crawjud.types.bot import (
    MessageTimeoutAutenticacao as MessageTimeoutAutenticacao,
)
from crawjud.types.pje import DictReturnDesafio, DictSeparaRegiao

if TYPE_CHECKING:
    from crawjud.types import BotData, T  # noqa: F401

load_dotenv()


def _kill_browsermob() -> None:
    import psutil

    keyword = "browsermob"
    matching_procs = []

    # Primeira fase: coleta segura
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        with suppress(
            psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception
        ):
            if any(keyword in part for part in proc.info["cmdline"]):
                matching_procs.append(proc)

    # Segunda fase: ação
    for proc in matching_procs:
        with suppress(psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            print(f"Matando PID {proc.pid} ({' '.join(proc.info['cmdline'])})")
            proc.kill()


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
        _regiao_session: dict[str, DictReturnAuth] = {}
        _tasks_queue_processos: list[AsyncResult] = []
        _process = list(psutil.process_iter())

        _start_time: datetime = formata_tempo(current_task.request.eta)
        _total_rows = len(_bot_data)
        for regiao, data_regiao in list(regioes["regioes"].items()):
            autenticacao_data: TReturnAuth = _task_autenticacao.apply_async(
                kwargs={"regiao": regiao}
            ).wait_ready()
            if isinstance(autenticacao_data, dict):
                kw_args = dict(autenticacao_data)

                kw_args.update({
                    "data": data_regiao,
                    "pid": _pid,
                    "regiao": regiao,
                    "start_time": _start_time.strftime("%d/%m/%Y, %H:%M:%S"),
                    "total_rows": _total_rows,
                    "position_process": _position_process,
                })
                _task_queue_processos = subtask(
                    "pje.queue_processos",
                ).apply_async(kwargs=kw_args)

                _tasks_queue_processos.append(_task_queue_processos)
                _kill_browsermob()

        print("ok")

    @staticmethod
    @shared_task(name="pje.queue_processos")
    def queue_processos(
        cookies: dict[str, str],  # noqa: D102
        headers: dict[str, str],
        base_url: str,
        data: list[BotData],
        pid: str,
        start_time: str,
        position_process: dict[str, int],
        total_rows: int = 0,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        """Enqueue processes for further processing."""
        for item in data:
            item["row"] = position_process[item["NUMERO_PROCESSO"]]
            item["total_rows"] = total_rows
            item["pid"] = pid
            item["url_base"] = base_url
            item["start_time"] = start_time
            resultados_busca: DictReturnDesafio = (
                subtask("pje.buscador")
                .apply_async(
                    kwargs={
                        "data": item,
                        "headers": headers,
                        "cookies": cookies,
                    }
                )
                .wait_ready()
            )

            subtask("save_cache").apply_async(
                kwargs={
                    "pid": pid,
                    "data": resultados_busca["results"]["data_request"],
                    "processo": item["NUMERO_PROCESSO"],
                }
            )
            pid = str(item["pid"])
            row = int(item["row"])
            start_time = item["start_time"]
            task_message = subtask("log_message")
            task_message.apply_async(
                kwargs={
                    "pid": pid,
                    "message": f"Informações do processo {item['NUMERO_PROCESSO']} salvas com sucesso!",
                    "row": row,
                    "type_log": "success",
                    "total_rows": item.get("total_rows", 0),
                    "start_time": start_time,
                }
            )

            print()
