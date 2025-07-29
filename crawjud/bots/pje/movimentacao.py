"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

import asyncio
import json
import re
import traceback
from asyncio import create_task, gather
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Any

import aiofiles
import requests
from celery import Celery, current_app
from dotenv import load_dotenv
from selenium.webdriver.common.by import By  # noqa: F401
from selenium.webdriver.support import expected_conditions as ec  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait

from common.bot import ClassBot
from crawjud._wrapper import wrap_init
from crawjud.bots.pje.res.autenticador import autenticar
from crawjud.bots.pje.res.buscador import buscar_processo
from crawjud.core._dictionary import BotData
from webdriver import DriverBot

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


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
        semaforo_regiao = asyncio.Semaphore(1)
        dataframe = self.dataFrame()
        frame = await self._separar_regiao(dataframe)
        self.total_rows = len(self.position_process)

        tasks = [
            create_task(self._queue_regiao(key, value, semaforo_regiao))
            for key, value in list(frame.items())
        ]
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
        async with semaforo_regiao:
            try:
                if self.is_stoped:
                    asyncio.current_task().cancel()

                if not self.driver_trt.get(regiao):
                    driver = DriverBot(
                        selected_browser="firefox",
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

                for value in data:
                    await self.queue(
                        data=value,
                        driver=driver,
                        wait=wait,
                        regiao=regiao,
                    )

                driver.quit()
            except Exception as e:
                print("\n".join(traceback.format_exception(e)))
                self.print_msg(
                    "Erro de operação",
                    type_log="error",
                )

    async def queue(  # noqa: D102
        self,
        data: BotData,
        driver: DriverBot,
        wait: WebDriverWait,
        regiao: str,
    ) -> None:
        if self.is_stoped:
            asyncio.current_task().cancel()

        try:
            row = int(self.position_process.get(str(data["NUMERO_PROCESSO"]))) + 1
            await buscar_processo(
                row=row,
                driver=driver,
                wait=wait,
                data=data,
                regiao=regiao,
                print_msg=self.print_msg,
                pid=self.pid,
            )
            await self.extrair_movimentacao(driver=driver, data=data, row=row)
            self.print_msg(
                "Execução realizada com sucesso!",
                row=row,
                type_log="success",
            )

        except Exception as e:
            print("\n".join(traceback.format_exception(e)))
            self.print_msg(
                "Erro de operação",
                row=row,
                type_log="error",
            )

    async def extrair_movimentacao(  # noqa: D102
        self,
        driver: DriverBot,
        row: int,
        data: BotData,
    ) -> None:
        self.print_msg(
            message="Extraindo movimentações do processo",
            type_log="info",
            row=row,
            pid=self.pid,
            status="Em Execução",
        )

        cookies = driver.get_cookies()

        _har_data = driver.current_HAR
        entries = list(_har_data.entries)
        entry_proxy = [
            item
            for item in entries
            if "pje-consulta-api/api/processos/" in item.request.url
            and re.match(
                r"^https:\/\/pje\.trt\d+\.jus\.br\/pje-consulta-api\/api\/processos\/\d+$",
                item.request.url,
            )
        ][-1]

        headers = {
            header["name"]: header["value"] for header in entry_proxy.request.headers
        }
        token_captcha = list(filter(lambda x: x["name"] == "tokenDesafio", cookies))
        token_captcha = token_captcha[-1]["value"]
        _cookies = {str(cookie["name"]): str(cookie["value"]) for cookie in cookies}

        response = requests.get(  # noqa: ASYNC210
            f"{entry_proxy.request.url}?tokenDesafio={token_captcha}&resposta={_cookies['respostaDesafio']}",
            cookies=_cookies,
            headers=headers,
            timeout=25,
        )
        _response2 = requests.get(  # noqa: ASYNC210
            f"{entry_proxy.request.url}/integra?tokenCaptcha={response.headers['captchatoken']}",
            cookies=_cookies,
            headers=headers,
            timeout=25,
        )

        async with aiofiles.open(
            Path(self.output_dir_path).joinpath(
                f"COPIA INTEGRAL {data['NUMERO_PROCESSO']} {self.pid}.pdf"
            ),
            "wb",
        ) as f:
            for _data_ in _response2.iter_content(4096):
                await f.write(_data_)

        _data_processo = response.json()

        _documentos: list[dict[str, str | Any]] = [
            item
            for item in _data_processo["itensProcesso"]
            if item["tipoConteudo"].upper() == "PDF"
        ]

        _movimentacao: list[dict[str, str | Any]] = [
            item
            for item in _data_processo["itensProcesso"]
            if item["tipoConteudo"].upper() == "HTML"
        ]

        args_task = {
            "pid": self.pid,
            "data": _movimentacao,
            "processo": data["NUMERO_PROCESSO"],
        }

        try:
            async with aiofiles.open(
                f"{data['NUMERO_PROCESSO']} - {self.pid}.json", "w"
            ) as f:
                await f.write(json.dumps(_data_processo))

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
