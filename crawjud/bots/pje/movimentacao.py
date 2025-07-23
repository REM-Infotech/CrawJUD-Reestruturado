"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

import asyncio
import base64
import io
import re
import traceback
from asyncio import Semaphore, create_task, gather, sleep
from contextlib import suppress
from typing import TYPE_CHECKING, Self

from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from addons.recaptcha import captcha_to_image
from crawjud.addons.interator import Interact
from crawjud.addons.webdriver import DriverBot
from crawjud.core import CrawJUD

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


load_dotenv()


class Movimentacao(CrawJUD):
    """Initialize and execute pauta operations for retrieving court hearing data now.

    Inherit from CrawJUD and manage the process of fetching pautas.
    """

    @classmethod
    async def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize a new Pauta instance with provided arguments now.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Returns:
            Self: A new instance of Pauta.

        """
        return cls(*args, **kwargs)

    async def execution(self) -> None:
        """Execute the main process loop to retrieve pautas until data range is covered now.

        This method continuously processes each court hearing date and handles errors.
        """
        semaphore = Semaphore(1)
        self.driver.quit()
        frame = self.dataFrame()
        self.max_rows = len(frame)

        tasks = [
            create_task(self._test(semaphore, pos + 1, value))
            for pos, value in enumerate(frame)
        ]
        await gather(*tasks)

    async def formata_url_pje(self, data: BotData, type_format: str = "login") -> str:
        numero_processo = data["NUMERO_PROCESSO"]
        trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()

        if trt_id.startswith("0"):
            trt_id = trt_id.replace("0", "")

        formats = {
            "login": f"https://pje.trt{trt_id}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{trt_id}.jus.br/pjekz/",
            "search": f"https://pje.trt{trt_id}.jus.br/consultaprocessual/",
        }

        return formats[type_format]

    async def autenticar(
        self, driver: WebDriver, wait: WebDriverWait, data: BotData
    ) -> None:
        url = await self.formata_url_pje(data)
        driver.get(url)
        btn_sso = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'button[id="btnSsoPdpj"]',
            ))
        )
        btn_sso.click()

        await sleep(5)

        btn_certificado = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                ('div[class="certificado"] > a'),
            ))
        )
        btn_certificado.click()

        WebDriverWait(driver, 60).until(
            ec.url_to_be(await self.formata_url_pje(data, "validate_login"))
        )

    async def buscar_processo(
        self,
        driver: WebDriver,
        wait: WebDriverWait,
        data: BotData,
        interact: Interact,
    ):
        url = await self.formata_url_pje(data, "search")
        driver.get(url)

        campo_processo = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[id="nrProcessoInput"]',
            ))
        )

        campo_processo.click()
        interact.send_key(campo_processo, data["NUMERO_PROCESSO"])

        btn_pesquisar = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'button[id="btnPesquisar"]',
            ))
        )
        btn_pesquisar.click()
        await self.desafio_captcha(driver, wait, interact)

    async def desafio_captcha(  # noqa: D102
        self,
        driver: WebDriver,
        wait: WebDriverWait,
        interact: Interact,
    ) -> None:
        tries = 0
        while tries < 5:
            img = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'img[id="imagemCaptcha"]',
                ))
            ).get_attribute("src")
            await asyncio.sleep(2)
            bytes_img = base64.b64decode(img.replace("data:image/png;base64, ", ""))
            readable_buffer = io.BytesIO(bytes_img)
            text = captcha_to_image(readable_buffer.read())
            await asyncio.sleep(2)
            input_captcha = driver.find_element(
                By.CSS_SELECTOR, 'input[id="captchaInput"]'
            )
            interact.send_key(input_captcha, text)
            await asyncio.sleep(2)

            btn_enviar = driver.find_element(
                By.CSS_SELECTOR, 'button[id="btnEnviar"]'
            )
            btn_enviar.click()

            pattern_url = r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+$"
            with suppress(Exception):
                WebDriverWait(driver, 10).until(ec.url_matches(pattern_url))
                break

            await sleep(2)
            tries += 1

    async def _test(
        self,
        semaphore: asyncio.Semaphore,
        pos: int,
        data: BotData,
    ) -> None:
        async with semaphore:
            driver, wait = DriverBot("gecko", execution_path=self.output_dir_path)()
            driver.maximize_window()
            try:
                pid = self.pid
                interator = Interact(driver, wait, pid)
                await self.autenticar(driver, wait, data)
                await self.buscar_processo(driver, wait, data, interator)
                await self.prt.print_msg(
                    "Execução realizada com sucesso!",
                    row=pos,
                    type_log="success",
                )

                await asyncio.sleep(2)
                driver.quit()

            except Exception as e:
                await self.prt.print_msg(
                    "\n".join(traceback.format_exception(e)),
                    row=pos,
                    type_log="error",
                )
