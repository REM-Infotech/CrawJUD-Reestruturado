"""Módulo de pesquisa Esaj."""

from __future__ import annotations

from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.addons.search import SearchController
from crawjud.common.exceptions.bot import ExecutionError


class EsajSearch(SearchController):
    """Classe de autenticação Esaj."""

    def search(self, bot_data: dict[str, str]) -> bool:
        """Procura processo no ESAJ.

        Returns:
           bool: True se encontrado; ou False
        Navega pela pagina do ESAJ, processa entradas com base no grau do processo.

        """
        self.bot_data = bot_data
        grau = self.bot_data.get("GRAU", 1)

        if not grau:
            grau = 1

        if isinstance(grau, str):
            if "º" in grau:
                grau = grau.replace("º", "").replace(" ", "")

            grau = int(grau)

        if grau == 1:
            self.driver.get(self.elements.consultaproc_grau1)
            id_consultar = "botaoConsultarProcessos"

        elif grau == 2:
            self.driver.get(self.elements.consultaproc_grau2)
            id_consultar = "pbConsultar"

        elif not grau or grau != 1 or grau != 2:
            raise ExecutionError(message="Informar instancia!")

        sleep(1)
        # Coloca o campo em formato "Outros" para inserir o número do processo
        ratioNumberOld: WebElement = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((By.ID, "radioNumeroAntigo"))
        )  # noqa: N806
        ratioNumberOld.click()

        # Insere o processo no Campo
        lineprocess: WebElement = self.wait.until(
            ec.presence_of_element_located((By.ID, "nuProcessoAntigoFormatado"))
        )
        lineprocess.click()
        lineprocess.send_keys(self.bot_data.get("NUMERO_PROCESSO"))

        # Abre o Processo
        openprocess = None
        with suppress(TimeoutException):
            openprocess: WebElement = self.wait.until(
                ec.presence_of_element_located((By.ID, id_consultar))
            )
            openprocess.click()

        check_process = None
        with suppress(NoSuchElementException, TimeoutException):
            check_process = WebDriverWait(self.driver, 5).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, "#numeroProcesso")),
            )

        # Retry 1
        if not check_process:
            with suppress(NoSuchElementException, TimeoutException):
                check_process: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'div[id="listagemDeProcessos"]',
                    )),
                )

                if check_process:
                    check_process = (
                        check_process.find_element(By.TAG_NAME, "ul")
                        .find_elements(By.TAG_NAME, "li")[0]
                        .find_element(By.TAG_NAME, "a")
                    )

                    url_proc = check_process.get_attribute("href")
                    self.driver.get(url_proc)

        # Retry 2
        if not check_process:
            with suppress(NoSuchElementException, TimeoutException):
                check_process: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            'div.modal__process-choice > input[type="radio"]',
                        ),
                    ),
                )

                if check_process:
                    check_process.click()
                    btEnviarIncidente = self.driver.find_element(  # noqa: N806
                        By.CSS_SELECTOR, 'input[name="btEnviarIncidente"]'
                    )  # noqa: N806
                    btEnviarIncidente.click()

        return check_process is not None
