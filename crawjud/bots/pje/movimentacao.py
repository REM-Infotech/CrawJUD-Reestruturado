"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

import asyncio
import json
import re
import traceback
from asyncio import create_task, gather, sleep
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiofiles
import httpx
from celery import Celery, current_app
from dotenv import load_dotenv
from selenium.webdriver.common.by import By  # noqa: F401
from selenium.webdriver.support import expected_conditions as ec  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait

from crawjud._wrapper import wrap_init
from crawjud.bots.pje.resources.autenticador import autenticar
from crawjud.bots.pje.resources.buscador import buscar_processo
from crawjud.common.bot import ClassBot
from crawjud.types import BotData
from utils.webdriver import DriverBot

if TYPE_CHECKING:
    from crawjud.types import BotData


load_dotenv()


@wrap_init
class Movimentacao(ClassBot):
    """Initialize and execute pauta operations for retrieving court hearing data now.

    Inherit from CrawJUD and manage the process of fetching pautas.
    """

    driver_trt: dict[str, dict[str, DriverBot | WebDriverWait]] = {}
    position_process: dict[str, int] = {}
    app: Celery = current_app

    async def format_trt(self, numero_processo: str) -> str:  # noqa: D102
        trt_id = None
        with suppress(Exception):
            trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()
            if trt_id.startswith("0"):
                trt_id = trt_id.replace("0", "")

        return trt_id

    async def _separar_regiao(self, frame: list[BotData]) -> dict[str, list[BotData]]:
        regioes_dict: dict[str, list[BotData]] = {}

        for item in frame:
            numero_processo = item["NUMERO_PROCESSO"]
            regiao = await self.format_trt(numero_processo)

            if not regiao:
                continue

            self.position_process[numero_processo] = len(self.position_process)
            if not regioes_dict.get(regiao):
                regioes_dict[regiao] = [item]
                continue

            regioes_dict[regiao].append(item)

        return regioes_dict

    async def execution(self) -> None:
        """Execute the main process loop to retrieve pautas until data range is covered now.

        This method continuously processes each court hearing date and handles errors.
        """
        semaforo_regiao = asyncio.Semaphore(5)
        dataframe = self.dataFrame()
        frame = await self._separar_regiao(dataframe)
        self.total_rows = len(self.position_process)
        self.max_rows = self.total_rows
        tasks = []
        for key, value in list(frame.items()):
            task = create_task(self._queue_regiao(key, value, semaforo_regiao))
            tasks.append(task)
            await sleep(30)

        await gather(*tasks)
        self.app.send_task(
            "save_succes",
            kwargs={"pid": self.pid, "filename": Path(self.planilha_sucesso).name},
        )

    async def _queue_regiao(
        self,
        regiao: str,
        data: list[BotData],
        semaforo_regiao: asyncio.Semaphore,
    ) -> None:
        driver = None
        async with semaforo_regiao:
            try:
                if self.is_stoped:
                    asyncio.current_task().cancel()

                if not self.driver_trt.get(regiao):
                    driver = DriverBot(
                        selected_browser="chrome",
                        execution_path=self.output_dir_path,
                        with_proxy=True,
                    )

                    wait = driver.wait

                    self.driver_trt[regiao] = {
                        "driver": driver,
                        "wait": wait,
                    }

                    driver.maximize_window()

                driver: DriverBot = self.driver_trt[regiao]["driver"]
                wait: WebDriverWait = self.driver_trt[regiao]["wait"]

                await autenticar(driver, wait, regiao)
                await sleep(5)

                cookies_driver = driver.get_cookies()
                _har_data = driver.current_HAR
                entries = list(_har_data.entries)
                entry_proxy = [
                    item
                    for item in entries
                    if f"https://pje.trt{regiao}.jus.br/pje-comum-api/"
                    in item.request.url
                ][-1]
                headers = {
                    header["name"]: header["value"]
                    for header in entry_proxy.request.headers
                }
                cookies = {
                    str(cookie["name"]): str(cookie["value"])
                    for cookie in cookies_driver
                }

                driver.quit()

                for value in data:
                    await self.queue(
                        data=value,
                        headers=headers,
                        cookies=cookies,
                        regiao=regiao,
                    )

            except Exception as e:
                msg = "\n".join(traceback.format_exception(e))
                self.print_msg(
                    message=f"Erro de operação\n{msg}",
                    pid=self.pid,
                    type_log="error",
                    status="Em Execução",
                )
                if driver:
                    with suppress(Exception):
                        driver.quit()

    async def queue(  # noqa: D102
        self,
        data: BotData,
        headers: dict[str, str],
        cookies: dict[str, str],
        regiao: str,
    ) -> None:
        if self.is_stoped:
            asyncio.current_task().cancel()

        try:
            row = int(self.position_process.get(str(data["NUMERO_PROCESSO"]))) + 1

            async with httpx.AsyncClient(
                timeout=25,
                base_url=f"https://pje.trt{regiao}.jus.br/pje-consulta-api/api",
                cookies=cookies,
                headers=headers,
            ) as client:
                _header, _cookie, results = await buscar_processo(
                    row=row,
                    client=client,
                    data=data,
                    print_msg=self.print_msg,
                    pid=self.pid,
                )
                await self.extrair_movimentacao(
                    client=client,
                    data=data,
                    row=row,
                    id_processo=results[0],
                    token_captcha=results[1],
                    resposta_captcha=results[2],
                    resultados_busca=results[3],
                    _header=_header,
                    _cookie=_cookie,
                )
                self.print_msg(
                    message="Execução realizada com sucesso!",
                    row=row,
                    pid=self.pid,
                    type_log="success",
                    status="Em Execução",
                )

        except Exception as e:
            msg = "\n".join(traceback.format_exception(e))
            self.print_msg(
                message=f"Erro de operação\n{msg}",
                row=row,
                pid=self.pid,
                type_log="error",
                status="Em Execução",
            )

    async def extrair_movimentacao(  # noqa: D102
        self,
        row: int,
        data: BotData,
        client: httpx.AsyncClient,
        id_processo: str,
        token_captcha: str,
        resposta_captcha: str,
        resultados_busca: dict[str, str],
        _header: Any,
        _cookie: Any,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.print_msg(
            message="Extraindo movimentações do processo",
            type_log="info",
            row=row,
            pid=self.pid,
            status="Em Execução",
        )
        _response2 = await client.get(
            f"/processos/{id_processo}/integra?tokenCaptcha={token_captcha}",
            headers=_header,
        )

        async with aiofiles.open(
            Path(self.output_dir_path).joinpath(
                f"COPIA INTEGRAL {data['NUMERO_PROCESSO']} {self.pid}.pdf"
            ),
            "wb",
        ) as f:
            async for _data_ in _response2.aiter_bytes(65536):
                await f.write(_data_)

        _documentos: list[dict[str, str | Any]] = [
            item
            for item in resultados_busca["itensProcesso"]
            if item["tipoConteudo"].upper() == "PDF"
        ]

        _movimentacao: list[dict[str, str | Any]] = [
            item
            for item in resultados_busca["itensProcesso"]
            if item["tipoConteudo"].upper() == "HTML"
        ]

        args_task = {
            "pid": self.pid,
            "data": resultados_busca,
            "processo": data["NUMERO_PROCESSO"],
        }

        try:
            async with aiofiles.open(
                Path(self.output_dir_path).joinpath(
                    f"{data['NUMERO_PROCESSO']} - {self.pid}.json"
                ),
                "w",
            ) as f:
                await f.write(json.dumps(resultados_busca, ensure_ascii=False))

        except Exception as e:
            print(e)

        self.app.send_task("save_cache", kwargs=args_task)
        self.print_msg(
            message="Informações salvas!",
            pid=self.pid,
            row=row,
            type_log="success",
            status="Em Execução",
        )
