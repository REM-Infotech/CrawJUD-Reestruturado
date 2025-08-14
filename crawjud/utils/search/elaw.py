"""Módulo de controle de pesquisa Elaw."""

from __future__ import annotations

from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.controllers.bots.systems.elaw import ElawBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class ElawSearch(ElawBot):
    """Classe de pesquisa Elaw."""

    def search(self, bot_data: dict[str, str]) -> bool:
        """Procura processo no elaw.

        Returns:
           bool: True se encontrado; ou False
        Navega pela pagina do ELAW, interwage com elementos, clica pra abrir processo.

        """
        self.bot_data = bot_data
        if (
            self.driver.current_url
            != "https://amazonas.elaw.com.br/processoList.elaw"
        ):
            self.driver.get("https://amazonas.elaw.com.br/processoList.elaw")

        campo_numproc: WebElement = self.wait.until(
            ec.presence_of_element_located((By.ID, "tabSearchTab:txtSearch")),
        )
        campo_numproc.clear()
        sleep(0.15)
        campo_numproc.send_keys(self.bot_data.get("NUMERO_PROCESSO"))

        self.driver.find_element(By.ID, "btnPesquisar").click()
        search_result: WebElement = self.wait.until(
            ec.presence_of_element_located((By.ID, "dtProcessoResults_data")),
        )

        open_proc = None
        with suppress(NoSuchElementException):
            open_proc = search_result.find_element(
                By.ID,
                "dtProcessoResults:0:btnProcesso",
            )

        sleep(1.5)

        diff_cad = str(self.typebot.upper()) != "CADASTRO"
        diff_complement = str(self.typebot.upper()) != "COMPLEMENT"
        if open_proc:
            chkTypeBot = diff_cad and diff_complement  # noqa: N806
            if chkTypeBot:
                clicked = False
                with suppress(StaleElementReferenceException):
                    open_proc.click()
                    clicked = True

                if not clicked:
                    self.wait.until(
                        ec.presence_of_element_located((
                            By.ID,
                            "dtProcessoResults_data",
                        )),
                    ).find_element(
                        By.ID,
                        "dtProcessoResults:0:btnProcesso",
                    ).click()

            return True

        return False
