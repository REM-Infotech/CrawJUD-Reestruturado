"""Executa o processamento da capa dos processos PJE.

Este módulo contém a classe Capa responsável por autenticar, enfileirar e
processar processos judiciais, além de realizar o download da cópia integral
dos processos e salvar os resultados no storage.

"""

from __future__ import annotations

import threading
import traceback
from contextlib import suppress
from threading import Semaphore
from typing import TYPE_CHECKING, ClassVar

from dotenv import load_dotenv
from httpx import Client

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.bots.systems.pje import PjeBot
from crawjud_app.bots.resources.formatadores import formata_tempo
from crawjud_app.custom.task import ContextTask
from crawjud_app.decorators import shared_task, wrap_cls

if TYPE_CHECKING:
    from concurrent.futures import Future
    from datetime import datetime

    from crawjud.interface.types import BotData
    from crawjud.interface.types.pje import DictResults
load_dotenv()


@shared_task(name="pje.capa", bind=True, base=ContextTask)
@wrap_cls
class Capa[T](PjeBot):  # noqa: D101
    tasks_queue_processos: ClassVar[list[Future]] = []

    def execution(
        self,
        name: str | None = None,
        system: str | None = None,
        current_task: ContextTask = None,
        storage_folder_name: str | None = None,
    ) -> None:
        """Executa o fluxo principal de processamento da capa dos processos PJE.

        Args:
            name (str | None): Nome do bot.
            system (str | None): Sistema do bot.
            current_task (ContextTask): Tarefa atual do Celery.
            storage_folder_name (str): Nome da pasta de armazenamento.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.

        """
        start_time: datetime = formata_tempo(str(current_task.request.eta))
        self.folder_storage = storage_folder_name
        self.current_task = current_task
        self.start_time = start_time.strftime("%d/%m/%Y, %H:%M:%S")
        self.pid = str(current_task.request.id)

        self.queue()

    def queue(self) -> None:
        # Autentica e processa cada região

        semaforo_regiao = Semaphore(4)
        generator_regioes = self.regioes()
        for regiao, data_regiao in generator_regioes:
            with semaforo_regiao:
                try:
                    self.print_msg(message=f"Autenticando no TRT {regiao}")
                    if self.autenticar():
                        self.print_msg(
                            message="Autenticado com sucesso!",
                            type_log="info",
                        )
                        thread_ = threading.Thread(
                            target=self.queue_processo,
                            kwargs={
                                "data": data_regiao,
                                "base_url": self.base_url,
                                "headers": self.headers,
                                "cookies": self.cookies,
                            },
                        )

                        thread_.start()

                except (ExecutionError, Exception) as e:
                    self.print_msg(
                        message="\n".join(traceback.format_exception(e)),
                        type_log="error",
                    )

    def queue_processo(
        self,
        data: BotData,
        base_url: str,
        headers: str,
        cookies: str,
    ) -> str:
        """Enfileira processos para processamento e salva resultados.

        Args:
            cookies (dict[str, str]): Cookies de autenticação.
            headers (dict[str, str]): Cabeçalhos HTTP.
            base_url (str): URL base do serviço.
            data (list[BotData]): Lista de dados dos processos.
            pid (str): Identificador do processo.
            start_time (str): Horário de início do processamento.
            position_process (dict[str, int]): Posições dos processos.
            total_rows (int): Total de linhas a processar.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.



        """
        semaforo_file = Semaphore(4)
        cl = Client(
            base_url=base_url,
            timeout=30,
            headers=headers,
            cookies=cookies,
            follow_redirects=True,
        )

        list_tasks: list[Future] = []

        with cl as client:
            for item in data:
                try:
                    # Atualiza dados do item para processamento
                    row = self.list_posicao_processo[item["NUMERO_PROCESSO"]]
                    resultado: DictResults = self.buscar_processo(
                        data=item,
                        row=row,
                        client=client,
                    )

                    if resultado:
                        data_request = resultado.get("data_request")
                        if data_request:
                            # Salva dados em cache
                            self.save_success_cache(
                                data=data_request,
                                processo=item["NUMERO_PROCESSO"],
                            )

                            thread_ = threading.Thread(
                                target=self.copia_integral,
                                kwargs={
                                    "row": row,
                                    "data": item,
                                    "client": client,
                                    "semaforo": semaforo_file,
                                    "id_processo": resultado["id_processo"],
                                    "captchatoken": resultado["captchatoken"],
                                },
                            )

                            list_tasks.append(
                                thread_,
                            )

                            thread_.start()

                            message = (
                                f"Informações do processo "
                                f"{item['NUMERO_PROCESSO']} salvas com sucesso!"
                            )
                            self.print_msg(
                                message=message,
                                row=row,
                                type_log="success",
                            )

                except (ExecutionError, Exception):
                    self.print_msg(
                        message="Erro ao buscar processo",
                        row=row,
                        type_log="error",
                    )

        for future in list_tasks:
            with suppress(Exception):
                future.result()

    def copia_integral(  # noqa: D417
        self,
        row: int,
        data: BotData,
        client: Client,
        semaforo: Semaphore,
        id_processo: str,
        captchatoken: str,
    ) -> None:
        """Realiza o download da cópia integral do processo e salva no storage.

        Args:
            pid: str: Identificador do processo.
            url_base (str): URL base do serviço.
            headers (dict[str, str]): Cabeçalhos HTTP.
            cookies (dict[str, str]): Cookies de autenticação.
            id_processo (str): Identificador do processo.
            captchatoken (str): Token do captcha.
            file_name (str): Nome do arquivo para salvar.
            *args (T): Argumentos variáveis.
            **kwargs (T): Argumentos nomeados variáveis.



        """
        file_name = f"COPIA INTEGRAL {data['NUMERO_PROCESSO']} {self.pid}.pdf"

        with semaforo:
            proc = data["NUMERO_PROCESSO"]
            id_proc = id_processo
            captcha = captchatoken

            link = f"/processos/{id_proc}/integra?tokenCaptcha={captcha}"
            try:
                message = f"Baixando arquivo do processo n.{proc}"
                self.print_msg(
                    message=message,
                    row=row,
                    type_log="log",
                )

                response = client.get(url=link)
                pdf_content = list(
                    filter(
                        lambda x: x[0].lower() == "content-type"
                        and x[1].lower() == "application/pdf",
                        list(response.headers.items()),
                    ),
                )
                if len(pdf_content) > 0:
                    self.save_file_downloaded(file_name, response=response, data=data)

            except (ExecutionError, Exception):
                msg = "Erro ao baixar arquivo"

                self.print_msg(message=msg, row=row, type_log="error")
