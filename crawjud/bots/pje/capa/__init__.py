# noqa: D104
from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING, Generic

import psutil
from dotenv import load_dotenv
from httpx import Client

from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask as ContextTask
from celery_app.types._celery._canvas import AsyncResult
from crawjud._wrapper import wrap_init
from crawjud.bots.resources.formatadores import formata_tempo
from crawjud.common.bot import ClassBot
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types.bot import (
    DictFiles,
    TReturnAuth,
)
from crawjud.types.bot import (
    DictReturnAuth as DictReturnAuth,
)
from crawjud.types.bot import (
    MessageTimeoutAutenticacao as MessageTimeoutAutenticacao,
)
from crawjud.types.pje import DictReturnDesafio, DictSeparaRegiao
from utils.storage import Storage

if TYPE_CHECKING:
    from crawjud.types import BotData, T  # noqa: F401

load_dotenv()


def _kill_browsermob() -> None:
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
    # task_download_files = subtask("crawjud.download_files")
    # task_autenticacao = subtask("pje.autenticador")
    # task_bot_data = subtask("crawjud.dataFrame")
    # task_separa_regiao = subtask("pje.separar_regiao")

    @classmethod
    def enviar_mensagem_log(  # noqa: D102
        cls,
        pid: str,
        message: str,
        row: int,
        type_log: str,
        total_rows: int,
        start_time: str,
    ) -> None:
        _task_message = subtask("log_message")
        _task_message.apply_async(
            kwargs={
                "pid": pid,
                "message": message,
                "row": row,
                "type_log": type_log,
                "total_rows": total_rows,
                "start_time": start_time,
            }
        )

    @shared_task(name="pje.capa", bind=True)
    def pje_capa(  # noqa: D102
        self,
        storage_folder_name: str,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        pid = str(self.request.id)
        start_time: datetime = formata_tempo(self.request.eta).strftime(
            "%d/%m/%Y, %H:%M:%S"
        )
        cls = Capa

        files_b64: list[DictFiles] = cls.task_download_files.apply_async(
            kwargs={"storage_folder_name": storage_folder_name}
        ).wait_ready()

        xlsx_key = list(filter(lambda x: x["file_suffix"] == ".xlsx", files_b64))
        if not xlsx_key:
            raise ExecutionError(
                bot_execution_id=pid, message="Nenhum arquivo Excel encontrado."
            )

        bot_data: list[BotData] = cls.task_bot_data.apply_async(
            kwargs={"base91_planilha": xlsx_key[0]["file_base91str"]}
        ).wait_ready()

        cls.enviar_mensagem_log(
            pid=pid,
            message="Planilha carregada!",
            row=0,
            type_log="info",
            total_rows=len(bot_data),
            start_time=start_time,
        )

        regioes: DictSeparaRegiao = cls.task_separa_regiao.apply_async(
            kwargs={"frame": bot_data}
        ).wait_ready()

        position_process = regioes["position_process"]
        tasks_queue_processos: list[AsyncResult] = []

        total_rows = len(bot_data)

        cls.enviar_mensagem_log(
            pid=pid,
            message="Realizando autenticação nos TRTs...",
            row=0,
            type_log="log",
            total_rows=len(bot_data),
            start_time=start_time,
        )

        for regiao, data_regiao in list(regioes["regioes"].items()):
            cls.enviar_mensagem_log(
                pid=pid,
                message=f"Autenticando no TRT {regiao}",
                row=0,
                type_log="log",
                total_rows=total_rows,
                start_time=start_time,
            )
            autenticacao_data: TReturnAuth = cls.task_autenticacao.apply_async(
                kwargs={"regiao": regiao}
            ).wait_ready()

            if isinstance(autenticacao_data, dict):
                kw_args = dict(autenticacao_data)
                kw_args.update({
                    "data": data_regiao,
                    "pid": pid,
                    "regiao": regiao,
                    "start_time": start_time,
                    "total_rows": total_rows,
                    "position_process": position_process,
                })

                # Inicia a fila de tarefas para processar os dados
                _task_queue_processos = subtask(
                    "pje.queue_processos",
                ).apply_async(kwargs=kw_args)

                # Armazena a tarefa na lista de tarefas
                tasks_queue_processos.append(_task_queue_processos)
                _kill_browsermob()

                # Envia mensagem de sucesso
                cls.enviar_mensagem_log(
                    pid=pid,
                    message="Autenticado com sucesso!",
                    row=0,
                    type_log="info",
                    total_rows=total_rows,
                    start_time=start_time,
                )

    @shared_task(name="pje.queue_processos", bind=True)
    def queue_processos(
        self,
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
        task_message = subtask("log_message")
        for item in data:
            with suppress(Exception):
                item["row"] = position_process[item["NUMERO_PROCESSO"]]
                item["total_rows"] = total_rows
                item["pid"] = pid
                item["url_base"] = base_url
                item["start_time"] = start_time
                row = int(item["row"]) + 1
                start_time = item["start_time"]
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

                if not resultados_busca or (
                    isinstance(resultados_busca, str)
                    and "Nenhum processo encontrado" in resultados_busca
                ):
                    task_message.apply_async(
                        kwargs={
                            "pid": pid,
                            "message": "Falha ao obter informações do processo ",
                            "row": row,
                            "type_log": "error",
                            "total_rows": item.get("total_rows", 0),
                            "start_time": start_time,
                        }
                    )
                    continue

                subtask("save_cache").apply_async(
                    kwargs={
                        "pid": pid,
                        "data": resultados_busca["results"]["data_request"],
                        "processo": item["NUMERO_PROCESSO"],
                    }
                )

                file_name = f"COPIA INTEGRAL {item['NUMERO_PROCESSO']} {pid}.pdf"
                subtask("pje.capa.copia_integral").apply_async(
                    kwargs={
                        "url_base": base_url,
                        "file_name": file_name,
                        "headers": headers,
                        "cookies": cookies,
                        "id_processo": resultados_busca["results"]["id_processo"],
                        "captchatoken": resultados_busca["results"]["captchatoken"],
                    }
                )

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

    @shared_task(name="pje.capa.copia_integral", bind=True)
    def download_copia_integral(  # noqa: D102
        self,
        url_base: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        id_processo: str,
        captchatoken: str,
        file_name: str,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        storage = Storage("minio")
        with suppress(Exception):
            with Client(
                base_url=url_base,
                timeout=30,
                headers=headers,
                cookies=cookies,
            ) as client:
                response = client.get(
                    url=f"/processos/{id_processo}/integra?tokenCaptcha={captchatoken}"
                )
                chunk = 65536
                _path_temp = Path(__file__).cwd().joinpath("temp", id_processo)
                total_chunks = ceil(len(response.content))

                for _bytes in response.iter_bytes(chunk):
                    content_lenght = len(_bytes)
                    storage.append_object(
                        file_name, _bytes, content_lenght, total_chunks
                    )
