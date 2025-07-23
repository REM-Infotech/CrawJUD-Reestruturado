"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

from __future__ import annotations

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
from crawjud.core._dictionary import BotData

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


load_dotenv()


class Movimentacao(CrawJUD):
    """Initialize and execute pauta operations for retrieving court hearing data now.

    Inherit from CrawJUD and manage the process of fetching pautas.
    """

    driver_trt: dict[str, dict[str, WebDriver | WebDriverWait | Interact]] = {}

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

    async def format_trt(self, numero_processo: str) -> str:  # noqa: D102
        trt_id = re.search(r"(?<=5\.)\d{2}", numero_processo).group()
        if trt_id.startswith("0"):
            trt_id = trt_id.replace("0", "")

        return trt_id

    async def _separar_regiao(self, frame: list[BotData]) -> dict[str, list[BotData]]:
        regioes_dict: dict[str, list[BotData]] = {}

        for item in frame:
            regiao = await self.format_trt(item["NUMERO_PROCESSO"])
            if not regioes_dict.get(regiao):
                regioes_dict.update({str(regiao): [item]})
                continue

            regioes_dict[regiao].append(item)

        return regioes_dict

    async def execution(self) -> None:
        """Execute the main process loop to retrieve pautas until data range is covered now.

        This method continuously processes each court hearing date and handles errors.
        """
        semaforo_regiao = Semaphore(5)
        self.driver.quit()
        frame = await self._separar_regiao(self.dataFrame())
        self.max_rows = len(frame)

        tasks = [
            create_task(self._queue_regiao(key, value, semaforo_regiao))
            for key, value in list(frame.items())
        ]
        await gather(*tasks)

    async def _queue_regiao(
        self,
        regiao: str,
        data: list[BotData],
        semaforo_regiao: Semaphore,
    ) -> None:
        pid = self.pid
        with semaforo_regiao:
            semaforo_processo = Semaphore(1)
            tasks = []

            if not self.driver_trt.get(regiao):
                driver, wait = DriverBot(
                    "chrome",
                    execution_path=self.output_dir_path,
                )()
                self.driver_trt[regiao] = {
                    "driver": driver,
                    "wait": wait,
                    "interact": Interact(driver, wait, pid),
                }

                driver.maximize_window()

            driver: WebDriver = self.driver_trt[regiao]["driver"]
            wait: WebDriverWait = self.driver_trt[regiao]["wait"]
            interator: Interact = self.driver_trt[regiao]["interact"]

            await self.autenticar(driver, wait, regiao)

            for pos, value in enumerate(data):
                row = pos + 1
                tasks.append(
                    create_task(
                        self._queue(
                            semaforo_processo=semaforo_processo,
                            pos=row,
                            data=value,
                            driver=driver,
                            wait=wait,
                            interator=interator,
                            regiao=regiao,
                        )
                    )
                )

            await gather(*tasks)

    async def _queue(
        self,
        semaforo_processo: Semaphore,
        pos: int,
        data: BotData,
        driver: WebDriver,
        wait: WebDriverWait,
        interator: Interact,
        regiao: str,
    ) -> None:
        async with semaforo_processo:
            try:
                await self.buscar_processo(
                    driver=driver,
                    wait=wait,
                    data=data,
                    interact=interator,
                    regiao=regiao,
                )
                await self.prt.print_msg(
                    "Execução realizada com sucesso!",
                    row=pos,
                    type_log="success",
                )

                await sleep(2)
                driver.quit()

            except Exception as e:
                await self.prt.print_msg(
                    "\n".join(traceback.format_exception(e)),
                    row=pos,
                    type_log="error",
                )

    async def extrair_movimentacao(  # noqa: D102
        self,
        driver: WebDriver,
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

        data = wait.until(
            ec.presence_of_all_elements_located((
                By.XPATH,
                "//tr[contains(@class, 'row-odd') or contains(@class, 'row-even')]",
            ))
        )

        for item in data:
            print(item)

    async def formata_url_pje(self, regiao: str, type_format: str = "login") -> str:  # noqa: D102
        formats = {
            "login": f"https://pje.trt{regiao}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{regiao}.jus.br/pjekz/",
            "search": f"https://pje.trt{regiao}.jus.br/consultaprocessual/",
        }

        return formats[type_format]

    async def autenticar(  # noqa: D102
        self, driver: WebDriver, wait: WebDriverWait, regiao: str
    ) -> None:
        url = await self.formata_url_pje(regiao)
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
        event_cert = btn_certificado.get_attribute("onclick")
        driver.execute_script(event_cert)

        WebDriverWait(driver, 60).until(
            ec.url_to_be(await self.formata_url_pje(regiao, "validate_login"))
        )

    async def buscar_processo(  # noqa: D102
        self,
        driver: WebDriver,
        wait: WebDriverWait,
        data: BotData,
        interact: Interact,
        regiao: str,
    ) -> None:
        url = await self.formata_url_pje(regiao, "search")
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
            await sleep(2)
            bytes_img = base64.b64decode(img.replace("data:image/png;base64, ", ""))
            readable_buffer = io.BytesIO(bytes_img)
            text = captcha_to_image(readable_buffer.read())
            await sleep(2)
            input_captcha = driver.find_element(
                By.CSS_SELECTOR, 'input[id="captchaInput"]'
            )
            interact.send_key(input_captcha, text)
            await sleep(2)

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
