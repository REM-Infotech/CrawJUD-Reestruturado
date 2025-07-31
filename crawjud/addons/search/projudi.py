"""Módulo de pesquisa CrawJUD."""

from contextlib import suppress
from datetime import datetime
from time import sleep
from typing import TYPE_CHECKING

import pytz
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.addons.search import SearchController
from crawjud.exceptions.bot import ExecutionError

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class ProjudiSearch(SearchController):
    """Classe de pesquisa PROJUDI."""

    def search(self, bot_data: dict[str, str]) -> bool:
        """Procura processos no PROJUDI.

        Returns:
            bool: True se encontrado; ou False
        redireciona pra cada rota apropriada

        """
        self.bot_data = bot_data
        url_search = self.elements.url_busca

        grau = self.bot_data.get("GRAU", 1) or 1

        if grau == 2:
            if not self.url_segunda_instancia:
                self.url_segunda_instancia = self.driver.find_element(
                    By.CSS_SELECTOR, 'a[id="Stm0p7i1eHR"]'
                ).get_attribute("href")

            url_search = self.url_segunda_instancia

        self.driver.get(url_search)

        if self.typebot != "proc_parte":
            return self.search_proc()

        return self.search_proc_parte()

    def search_proc(self) -> bool:
        """Pesquisa processo no PROJUDI.

        Returns:
            bool: True se encontrado; ou False
        manipula entradas, clique e tentativa condicional

        """
        inputproc = None
        enterproc = None
        allowacess = None
        not_found = None
        to_grau2 = None
        grau = self.bot_data.get("GRAU", 1) or 1

        if isinstance(grau, str):
            grau = grau.strip()

        grau = int(grau)

        def detect_intimacao() -> None:
            if "intimacaoAdvogado.do" in self.driver.current_url:
                raise ExecutionError(
                    message="Processo com Intimação pendente de leitura!"
                )

        def allow_access() -> None:
            with suppress(TimeoutException, NoSuchElementException):
                nonlocal allowacess
                allowacess = self.driver.find_element(
                    By.CSS_SELECTOR, "#habilitacaoProvisoriaButton"
                )

            if allowacess:
                allowacess.click()
                sleep(1)

                confirmterms = self.driver.find_element(
                    By.CSS_SELECTOR, "#termoAceito"
                )
                confirmterms.click()
                sleep(1)

                save = self.driver.find_element(By.CSS_SELECTOR, "#saveButton")
                save.click()

        def get_link_grau2() -> str | None:
            """Recupera link para acessar processos em segundo grau.

            Filtra elemento com "Clique aqui para visualizar os recursos relacionados".

            Returns:
                str | None: link ou None.

            """
            with suppress(Exception, TimeoutException, NoSuchElementException):
                info_proc = self.wait.until(
                    ec.presence_of_all_elements_located(
                        (
                            By.CSS_SELECTOR,
                            "table#informacoesProcessuais > tbody > tr > td > a",
                        ),
                    ),
                )

                info_proc = list(
                    filter(
                        lambda x: "Clique aqui para visualizar os recursos relacionados"
                        in x.text,
                        info_proc,
                    ),
                )[-1]

                return info_proc.get_attribute("href")

            return None

        if grau == 1:
            with suppress(TimeoutException):
                inputproc: WebElement = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "#numeroProcesso",
                    )),
                )

        elif grau == 2:
            with suppress(TimeoutException):
                inputproc = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "#numeroRecurso",
                    )),
                )

        if inputproc:
            proc = self.bot_data.get("NUMERO_PROCESSO")
            inputproc.send_keys(proc)
            sleep(1)
            consultar = self.driver.find_element(By.CSS_SELECTOR, "#pesquisar")
            consultar.click()

            with suppress(TimeoutException, NoSuchElementException, Exception):
                not_found = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        '//*[@id="buscaProcessosQualquerInstanciaForm"]/table[2]/tbody/tr/td',
                    ))
                )

            if not_found and not_found.text == "Nenhum registro encontrado":
                return False

            with suppress(TimeoutException):
                enterproc: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((By.CLASS_NAME, "link"))
                )

            if not enterproc:
                return False

            enterproc.click()

            # if grau == 1:
            #     to_grau2 = get_link_grau2()

            detect_intimacao()
            allow_access()

            if grau == 2 and to_grau2:
                self.driver.get(to_grau2)

            return True

        return False

    def search_proc_parte(self) -> bool:
        """Busca no PROJUDI nome da parte processual.

        Returns:
            bool: True se encontrado ou False.

        Insere dados, documento e gerencia pesquisa.

        """
        allprocess = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[value="qualquerAdvogado"]',
            )),
        )
        allprocess.click()
        data_inicio_xls = self.data_inicio
        data_fim_xls = self.data_fim

        if type(data_inicio_xls) is str:
            data_inicio_xls = datetime.strptime(data_inicio_xls, "%Y-%m-%d").replace(
                tzinfo=pytz.timezone("America/Manaus")
            )
            data_inicio_xls = data_inicio_xls.strftime("%d/%m/%Y")

        if type(data_fim_xls) is str:
            data_fim_xls = datetime.strptime(data_fim_xls, "%Y-%m-%d").replace(
                tzinfo=pytz.timezone("America/Manaus")
            )
            data_fim_xls = data_fim_xls.strftime("%d/%m/%Y")

        if self.vara == "TODAS AS COMARCAS":
            alljudge = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="pesquisarTodos"]',
                )),
            )
            alljudge.click()

        elif self.vara != "TODAS AS COMARCAS":
            search_vara = self.driver.find_element(By.ID, "descricaoVara")
            search_vara.click()
            search_vara.send_keys(self.vara)
            sleep(3)
            vara_option = self.driver.find_element(
                By.ID, "ajaxAuto_descricaoVara"
            ).find_elements(By.TAG_NAME, "li")[0]
            vara_option.click()

        sleep(3)
        input_parte = self.driver.find_element(
            By.CSS_SELECTOR, 'input[name="nomeParte"]'
        )
        input_parte.send_keys(self.parte_name)

        cpfcnpj = self.driver.find_element(By.CSS_SELECTOR, 'input[name="cpfCnpj"]')
        cpfcnpj.send_keys(self.doc_parte)

        data_inicio = self.driver.find_element(
            By.CSS_SELECTOR, 'input[id="dataInicio"]'
        )
        data_inicio.send_keys(data_inicio_xls)

        data_fim = self.driver.find_element(By.CSS_SELECTOR, 'input[name="dataFim"]')
        data_fim.send_keys(data_fim_xls)

        if self.polo_parte.lower() == "reu":
            setréu = self.driver.find_element(
                By.CSS_SELECTOR, 'input[value="promovido"]'
            )
            setréu.click()

        elif self.polo_parte.lower() == "autor":
            setautor = self.driver.find_element(
                By.CSS_SELECTOR, 'input[value="promovente"'
            )
            setautor.click()

        procenter = self.driver.find_element(By.ID, "pesquisar")
        procenter.click()
        sleep(3)

        with suppress(TimeoutException):
            enterproc: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CLASS_NAME, "link"))
            )

        if enterproc:
            return True

        return False
