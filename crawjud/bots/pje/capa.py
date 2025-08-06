# noqa: D100
from __future__ import annotations

import threading
import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress
from datetime import datetime
from os import path
from pathlib import Path
from typing import TYPE_CHECKING, Generic

from clear import clear
from dotenv import load_dotenv
from httpx import Client
from pytz import timezone

from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask
from crawjud.bot import ClassBot
from crawjud.bots.resources.formatadores import formata_tempo
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types.bot import (
    DictFiles,
    TReturnAuth,
)
from crawjud.types.pje import DictReturnDesafio, DictSeparaRegiao
from crawjud.wrapper import wrap_cls
from utils.storage import Storage

if TYPE_CHECKING:
    from crawjud.types import BotData, T  # noqa: F401


load_dotenv()


@shared_task(name="pje.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa(ClassBot, ContextTask):  # noqa: D101
    tasks_queue_processos: list[Future] = []

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
        self.current_task = current_task
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

        clear()

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

        total_rows = len(bot_data)

        semaforo = threading.Semaphore(8)

        with ThreadPoolExecutor(8) as executor:
            for regiao, data_regiao in list(regioes["regioes"].items()):
                if self.stop_bot:
                    break

                try:
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
                    if not isinstance(autenticacao_data, dict):
                        self.print_msg(
                            message=str(autenticacao_data),
                            pid=pid,
                            row=len(data_regiao),
                            type_log="error",
                            total_rows=total_rows,
                            start_time=start_time,
                            errors=len(data_regiao),
                        )
                        continue

                    # Envia mensagem de sucesso
                    self.print_msg(
                        pid=pid,
                        message="Autenticado com sucesso!",
                        row=0,
                        type_log="info",
                        total_rows=total_rows,
                        start_time=start_time,
                    )

                    kw_args = dict(autenticacao_data)
                    kw_args.update({
                        "data": data_regiao,
                        "pid": pid,
                        "regiao": regiao,
                        "start_time": start_time,
                        "total_rows": total_rows,
                        "position_process": position_process,
                        "semaforo": semaforo,
                    })

                    task = executor.submit(self.queue_processo, **kw_args)
                    self.tasks_queue_processos.append(task)

                except Exception as e:
                    self.print_msg(
                        message="\n".join(traceback.format_exception(e)),
                        pid=pid,
                        row=0,
                        type_log="error",
                        total_rows=total_rows,
                        start_time=start_time,
                    )

        for task in self.tasks_queue_processos:
            with suppress(Exception):
                task.result()

    def queue_processo(  # noqa: D417
        self,
        semaforo: threading.Semaphore,
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
    ) -> str:
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
        try:
            semaforo.acquire()

            def print_erro() -> None:
                self.print_msg(
                    pid=pid,
                    message="Falha ao obter informações do processo ",
                    row=row,
                    type_log="error",
                    total_rows=item.get("total_rows", 0),
                    start_time=start_time,
                )

            semaforo2 = threading.Semaphore(4)

            with ThreadPoolExecutor(4) as executor:
                for item in data:
                    if self.stop_bot:
                        break
                    try:
                        # Atualiza dados do item para processamento

                        item.update({
                            "row": position_process[item["NUMERO_PROCESSO"]] + 1,
                            "total_rows": total_rows,
                            "pid": pid,
                            "url_base": base_url,
                            "start_time": start_time,
                        })

                        row = int(item["row"])
                        start_time = item["start_time"]
                        resultados_busca: DictReturnDesafio = self.buscar_processo(
                            data=item, headers=headers, cookies=cookies
                        )

                        # Verifica se houve resultado na busca

                        # Verifica se resultados_busca é válido e possui dados
                        results = (
                            resultados_busca.get("results")
                            if isinstance(resultados_busca, dict)
                            else None
                        )
                        data_request = (
                            results.get("data_request") if results else None
                        )

                        if not data_request:
                            print_erro()
                            continue

                        # Salva dados em cache
                        self.save_success_cache(
                            data={
                                "pid": pid,
                                "data": resultados_busca["results"]["data_request"],
                                "processo": item["NUMERO_PROCESSO"],
                            }
                        )

                        file_name = (
                            f"COPIA INTEGRAL {item['NUMERO_PROCESSO']} {pid}.pdf"
                        )
                        _ft = executor.submit(
                            self.copia_integral,
                            semaforo=semaforo2,
                            pid=pid,
                            data=item,
                            total_rows=total_rows,
                            row=row,
                            url_base=base_url,
                            file_name=file_name,
                            headers=headers,
                            start_time=start_time,
                            cookies=cookies,
                            id_processo=resultados_busca["results"]["id_processo"],
                            captchatoken=resultados_busca["results"]["captchatoken"],
                        )

                        self.print_msg(
                            pid=pid,
                            message=f"Informações do processo {item['NUMERO_PROCESSO']} salvas com sucesso!",
                            row=row,
                            type_log="success",
                            total_rows=item.get("total_rows", 0),
                            start_time=start_time,
                        )

                    except Exception:
                        self.print_msg(
                            message="Erro ao buscar processo",
                            pid=pid,
                            row=row,
                            type_log="error",
                            total_rows=item.get("total_rows", 0),
                            start_time=start_time,
                        )

        finally:
            semaforo.release()

    def copia_integral(  # noqa: D417
        self,
        semaforo: threading.Semaphore,
        data: BotData,
        pid: str,
        row: int,
        total_rows: int,
        start_time: str,
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
        self.current_task = kwargs.get("current_task")
        storage = Storage("minio")

        try:
            semaforo.acquire()
            with Client(
                base_url=url_base,
                timeout=30,
                headers=headers,
                cookies=cookies,
            ) as client:
                try:
                    self.print_msg(
                        message=f"Baixando arquivo do processo n.{data['NUMERO_PROCESSO']}",
                        pid=pid,
                        row=row,
                        type_log="info",
                        total_rows=total_rows,
                        start_time=start_time,
                    )
                    response = client.get(
                        url=f"/processos/{id_processo}/integra?tokenCaptcha={captchatoken}"
                    )
                    chunk = 65536
                    _path_temp = Path(__file__).cwd().joinpath("temp", pid)

                    content_type = response.headers.get(
                        "Content-Type", headers.get("Content-Type", None)
                    )

                    if not content_type or content_type.lower() != "application/pdf":
                        return

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

                    self.print_msg(
                        message=f"Arquivo do processo n.{data['NUMERO_PROCESSO']} baixado com sucesso!",
                        pid=pid,
                        row=row,
                        type_log="success",
                        total_rows=total_rows,
                        start_time=start_time,
                    )
                except Exception:
                    msg = "Erro ao baixar arquivo"

                    self.print_msg(
                        message=msg,
                        pid=pid,
                        row=row,
                        type_log="error",
                        total_rows=total_rows,
                        start_time=start_time,
                    )
        finally:
            semaforo.release()
