# noqa: D100
from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from os import path
from pathlib import Path
from typing import TYPE_CHECKING, Generic

import psutil
from dotenv import load_dotenv
from httpx import Client
from pytz import timezone

from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask
from celery_app.types._celery._canvas import AsyncResult
from crawjud.bots.resources.formatadores import formata_tempo
from crawjud.common.bot import ClassBot
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types.bot import (
    DictFiles,
    TReturnAuth,
)
from crawjud.types.pje import DictReturnDesafio, DictSeparaRegiao
from utils.storage import Storage

if TYPE_CHECKING:
    from crawjud.types import BotData, T  # noqa: F401

load_dotenv()


def _kill_browsermob() -> None:
    """
    Finaliza processos relacionados ao BrowserMob Proxy.

    Args:
        None

    Returns:
        None: Não retorna valor.

    """
    keyword = "browsermob"
    matching_procs = []

    # Primeira fase: coleta segura dos processos
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        with suppress(
            psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, Exception
        ):
            if any(keyword in part for part in proc.info["cmdline"]):
                matching_procs.append(proc)

    # Segunda fase: finalização dos processos encontrados
    for proc in matching_procs:
        with suppress(psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            print(f"Matando PID {proc.pid} ({' '.join(proc.info['cmdline'])})")
            proc.kill()


@shared_task(name="pje.capa", bind=True, base=ContextTask)
class Capa(ContextTask, ClassBot):
    """
    Classe principal para processamento da capa dos processos PJE.

    Gerencia autenticação, separação de regiões e download de arquivos.
    """

    def __init__(  # noqa: D107
        self,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        self.execution(*args, **kwargs)

    def execution(
        self,
        current_task: ContextTask = None,
        storage_folder_name: str = None,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:  # noqa: D102
        """
        Executa o fluxo principal de processamento da capa dos processos PJE.

        Args:
            current_task (ContextTask): Tarefa atual do Celery.
            storage_folder_name (str): Nome da pasta de armazenamento.
            *args (Generic[T]): Argumentos variáveis.
            **kwargs (Generic[T]): Argumentos nomeados variáveis.

        Returns:
            None: Não retorna valor.

        Raises:
            ExecutionError: Caso não encontre arquivo Excel.

        """
        task_download_files = subtask("crawjud.download_files")
        task_bot_data = subtask("crawjud.dataFrame")
        pid = str(current_task.request.id)
        current_task.request.eta = datetime.now(timezone("America/Manaus"))
        start_time: str = formata_tempo(current_task.request.eta).strftime(
            "%d/%m/%Y, %H:%M:%S"
        )

        # Baixa arquivos da pasta de armazenamento
        files_b64: list[DictFiles] = task_download_files.apply_async(
            kwargs={"storage_folder_name": storage_folder_name}
        ).wait_ready()

        # Filtra arquivo Excel
        xlsx_key = list(filter(lambda x: x["file_suffix"] == ".xlsx", files_b64))
        if not xlsx_key:
            raise ExecutionError(
                bot_execution_id=pid, message="Nenhum arquivo Excel encontrado."
            )

        # Carrega dados da planilha
        bot_data: list[BotData] = task_bot_data.apply_async(
            kwargs={"base91_planilha": xlsx_key[0]["file_base91str"]}
        ).wait_ready()

        self.print_msg(
            pid=pid,
            message="Planilha carregada!",
            row=0,
            type_log="info",
            total_rows=len(bot_data),
            start_time=start_time,
        )

        # Separa dados por região
        self.print_msg(
            pid=pid,
            message="Realizando autenticação nos TRTs...",
            row=0,
            type_log="log",
            total_rows=len(bot_data),
            start_time=start_time,
        )

        self.queue(bot_data, pid, start_time)

    def queue(self, bot_data: list[BotData], pid: str, start_time: str) -> None:  # noqa: D102
        # Autentica e processa cada região
        task_separa_regiao = subtask("pje.separar_regiao")
        task_autenticacao = subtask("pje.autenticador")

        regioes: DictSeparaRegiao = task_separa_regiao.apply_async(
            kwargs={"frame": bot_data}
        ).wait_ready()

        position_process = regioes["position_process"]
        tasks_queue_processos: list[AsyncResult] = []

        total_rows = len(bot_data)

        for regiao, data_regiao in list(regioes["regioes"].items()):
            self.print_msg(
                pid=pid,
                message=f"Autenticando no TRT {regiao}",
                row=0,
                type_log="log",
                total_rows=total_rows,
                start_time=start_time,
            )
            autenticacao_data: TReturnAuth = task_autenticacao.apply_async(
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
                _task_queue_processos = QueueProcessos.apply_async(kwargs=kw_args)

                # Armazena a tarefa na lista de tarefas
                tasks_queue_processos.append(_task_queue_processos)
                _kill_browsermob()

                # Envia mensagem de sucesso
                self.print_msg(
                    pid=pid,
                    message="Autenticado com sucesso!",
                    row=0,
                    type_log="info",
                    total_rows=total_rows,
                    start_time=start_time,
                )


@shared_task(name="pje.queue_processos", base=ContextTask, bind=True)
class QueueProcessos(ContextTask, ClassBot):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        self.queue(*args, **kwargs)

    def execution(self, *args: Generic[T], **kwargs: Generic[T]) -> None:  # noqa: D102
        pass

    def queue(
        self,
        cookies: dict[str, str],
        headers: dict[str, str],
        base_url: str,
        data: list["BotData"],
        pid: str,
        start_time: str,
        position_process: dict[str, int],
        total_rows: int = 0,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        """
        Enfileira processos para processamento e salva resultados.

        Args:
            cookies (dict[str, str]): Cookies de autenticação.
            headers (dict[str, str]): Cabeçalhos HTTP.
            base_url (str): URL base do serviço.
            data (list[BotData]): Lista de dados dos processos.
            pid (str): Identificador do processo.
            start_time (str): Horário de início do processamento.
            position_process (dict[str, int]): Posições dos processos.
            total_rows (int): Total de linhas a processar.
            *args (Generic[T]): Argumentos variáveis.
            **kwargs (Generic[T]): Argumentos nomeados variáveis.

        Returns:
            None: Não retorna valor.

        """
        for item in data:
            with suppress(Exception):
                # Atualiza dados do item para processamento

                item.update({
                    "row": position_process[item["NUMERO_PROCESSO"]],
                    "total_rows": total_rows,
                    "pid": pid,
                    "url_base": base_url,
                    "start_time": start_time,
                })

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

                # Verifica se houve resultado na busca
                if (
                    not resultados_busca
                    or (
                        isinstance(resultados_busca, str)
                        and "Nenhum processo encontrado" in resultados_busca
                    )
                    or "Processo não encontrado" in resultados_busca
                ):
                    self.print_msg(
                        pid=pid,
                        message="Falha ao obter informações do processo ",
                        row=row,
                        type_log="error",
                        total_rows=item.get("total_rows", 0),
                        start_time=start_time,
                    )
                    continue

                # Salva dados em cache
                subtask("save_cache").apply_async(
                    kwargs={
                        "pid": pid,
                        "data": resultados_busca["results"]["data_request"],
                        "processo": item["NUMERO_PROCESSO"],
                    }
                )

                file_name = f"COPIA INTEGRAL {item['NUMERO_PROCESSO']} {pid}.pdf"
                DownloadCopiaIntegral.apply_async(
                    kwargs={
                        "pid": pid,
                        "url_base": base_url,
                        "file_name": file_name,
                        "headers": headers,
                        "cookies": cookies,
                        "id_processo": resultados_busca["results"]["id_processo"],
                        "captchatoken": resultados_busca["results"]["captchatoken"],
                    }
                )

                self.print_msg(
                    pid=pid,
                    message=f"Informações do processo {item['NUMERO_PROCESSO']} salvas com sucesso!",
                    row=row,
                    type_log="success",
                    total_rows=item.get("total_rows", 0),
                    start_time=start_time,
                )

                print()


@shared_task(name="pje.capa.copia_integral", bind=True)
class DownloadCopiaIntegral(ContextTask, ClassBot):  # noqa: D101
    def __init__(  # noqa: D107
        self,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        self.download_copia_integral(*args, **kwargs)

    def queue(self) -> None:  # noqa: D102
        pass

    def execution(self) -> None:  # noqa: D102
        pass

    def download_copia_integral(
        self,
        pid: str,
        url_base: str,
        headers: dict[str, str],
        cookies: dict[str, str],
        id_processo: str,
        captchatoken: str,
        file_name: str,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        """
        Realiza o download da cópia integral do processo e salva no storage.

        Args:
            pid: str: Identificador do processo.
            url_base (str): URL base do serviço.
            headers (dict[str, str]): Cabeçalhos HTTP.
            cookies (dict[str, str]): Cookies de autenticação.
            id_processo (str): Identificador do processo.
            captchatoken (str): Token do captcha.
            file_name (str): Nome do arquivo para salvar.
            *args (Generic[T]): Argumentos variáveis.
            **kwargs (Generic[T]): Argumentos nomeados variáveis.

        Returns:
            None: Não retorna valor.

        """
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
                _path_temp = Path(__file__).cwd().joinpath("temp", pid, id_processo)

                _path_temp.mkdir(exist_ok=True, parents=True)

                file_path = _path_temp.joinpath(file_name)
                # Salva arquivo em chunks no storage
                for pos, _bytes in enumerate(response.iter_bytes(chunk)):
                    mode = "ab"
                    if pos == 0:
                        mode = "wb"

                    with file_path.open(mode) as f:
                        f.write(_bytes)

                file_size = path.getsize(file_path)
                dest_name = path.join(pid.upper(), file_name)

                with file_path.open("rb") as file:
                    storage.put_object(
                        object_name=dest_name,
                        data=file,
                        length=file_size,
                    )
