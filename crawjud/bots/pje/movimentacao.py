"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

import asyncio
import re
import traceback
from asyncio import create_task, gather
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from celery import Celery, current_app
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from common.bot import ClassBot
from crawjud._wrapper import wrap_init
from crawjud.addons.interator import Interact
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

    driver_trt: dict[str, dict[str, WebDriver | WebDriverWait | Interact]] = {}
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
            if self.is_stoped:
                asyncio.current_task().cancel()

            if not self.driver_trt.get(regiao):
                driver = DriverBot(
                    selected_browser="chrome",
                    execution_path=self.output_dir_path,
                )

                wait = driver.wait

                self.driver_trt[regiao] = {
                    "driver": driver,
                    "wait": wait,
                }

                driver.maximize_window()

            driver: WebDriver = self.driver_trt[regiao]["driver"]
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

    async def queue(  # noqa: D102
        self,
        data: BotData,
        driver: WebDriver,
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
            )
            await self.extrair_movimentacao(
                regiao=regiao, driver=driver, wait=wait, data=data, row=row
            )
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
        driver: WebDriver,
        row: int,
        regiao: str,
        wait: WebDriverWait,
        data: BotData,
    ) -> None:
        btn_modo_tabela = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'button[aria-label="Visualizar em Tabela"]',
            ))
        )
        btn_modo_tabela.click()

        data_row = wait.until(
            ec.presence_of_all_elements_located((
                By.XPATH,
                "//tr[contains(@class, 'row-odd') or contains(@class, 'row-even')]",
            ))
        )

        movimentacoes: list[dict[str, str | datetime]] = []

        for item in data_row:
            try:
                data_td = item.find_elements(By.TAG_NAME, "td")
                split_time = data_td[1].text.split(" ")
                data_movimentacao = datetime.strptime(
                    f"{split_time[0]}/{split_time[1]} {split_time[2]}",
                    "%d/%m/%Y %H:%M",
                )
                if len(data_td) == 5:
                    id_movimentacao = "Sem ID"
                    descricao_movimentacao = data_td[3].text

                elif len(data_td) == 6:
                    id_movimentacao = data_td[3].text
                    descricao_movimentacao = data_td[4].text

                to_save = {
                    "PROCESSO": data["NUMERO_PROCESSO"],
                    "DATA": data_movimentacao,
                    "TIPO": data_td[2].text,
                    "MOVIMENTACAO_ID": id_movimentacao,
                    "DESCRIÇÃO": descricao_movimentacao,
                }

                movimentacoes.append(to_save)

            except Exception as e:
                print(e)
                continue

        args_task = {
            "pid": self.pid,
            "data": movimentacoes,
            "filename": f"EXECUÇÃO {self.pid}.xlsx",
            "sheet_name": f"TRT{regiao.zfill(2)}",
        }

        args_task = {
            "pid": self.pid,
            "data": movimentacoes,
            "processo": data["NUMERO_PROCESSO"],
        }
        self.app.send_task("save_cache", kwargs=args_task)
