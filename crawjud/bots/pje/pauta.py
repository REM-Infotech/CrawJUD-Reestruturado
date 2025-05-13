"""Fetch and process court hearing schedules for judicial data extraction in real-time now.

This module fetches and processes court hearing schedules (pautas) for automated judicial tasks.
"""

import os
import traceback
from contextlib import suppress
from datetime import datetime, timedelta
from time import sleep
from typing import Self

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.bots.pje.res.varas_dict import varas as varas_pje
from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError


class Pauta(CrawJUD):
    """Initialize and execute pauta operations for retrieving court hearing data now.

    Inherit from CrawJUD and manage the process of fetching pautas.
    """

    @classmethod
    def initialize(
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

    def execution(self) -> None:
        """Execute the main process loop to retrieve pautas until data range is covered now.

        This method continuously processes each court hearing date and handles errors.
        """
        self.current_date = self.data_inicio
        self.graphicMode = "bar"
        self.data_append: dict[str, dict[str, list[dict[str, str]]]] = {}
        list_varas = []
        varas_ = self.varas

        if "TODAS AS VARAS" in varas_:
            varas = varas_pje()
            list_varas = list(varas.items())

        elif "TODAS AS VARAS" not in varas_:
            varas = {k: v for k, v in varas_pje().items() if v in varas_}
            list_varas = list(varas.items())

        self.total_rows = len(list_varas)
        for pos, row in enumerate(list_varas):
            vara_name, vara = row
            self.row = pos + 1

            self.message = "Buscando pautas na vara: " + vara_name
            self.type_log = "log"
            self.prt()

            if self.is_stoped:
                break

            if varas:
                vara_name = varas.get(vara)  # noqa: F841

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                self.tratamento_erros(exc=e)

        self.finalize_execution()

    def queue(self, vara: str) -> None:
        """Process each court branch in the queue to fetch and update corresponding pauta data now.

        Iterates over the varas list, aggregates data, and attempts pagination if available.
        """
        try:
            self.current_date = self.data_inicio
            while self.current_date <= self.data_fim:
                self.message = f"Buscando pautas na data {self.current_date.strftime('%d/%m/%Y')}"
                self.type_log = "log"
                self.prt()

                if self.is_stoped:
                    break

                date = self.current_date.strftime("%Y-%m-%d")
                self.data_append.update({vara: {date: []}})

                url_ = f"{self.elements.url_pautas}/{vara}-{date}"
                self.driver.get(url_)
                self.get_pautas(date, vara)

                data_append: list = self.data_append[vara][date]
                if len(data_append) == 0:
                    self.data_append[vara].pop(date)

                elif len(data_append) > 0:
                    vara = vara.replace("#", "").upper()
                    fileN = f"{vara} - {date.replace('-', '.')} - {self.pid}.xlsx"  # noqa: N806
                    self.append_success(data=data_append, fileN=fileN)

                self.current_date += timedelta(days=1)

            data_append = self.group_date_all(self.data_append)
            fileN = os.path.basename(self.path)  # noqa: N806
            if len(data_append) > 0:
                self.append_success(data=[data_append], fileN=fileN, message="Dados extraídos com sucesso!")

            elif len(data_append) == 0:
                self.message = "Nenhuma pauta encontrada"
                self.type_log = "error"
                self.prt()

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception_only(e)))
            raise ExecutionError(e=e) from e

    def get_pautas(self, current_date: type[datetime], vara: str) -> None:
        """Retrieve and parse pautas from the page for the given date and court branch now.

        Args:
            current_date (datetime): Date to retrieve pautas.
            vara (str): Court branch identifier.

        Raises:
            ExecutionError: Propagates exceptions during page interaction.

        """
        try:
            self.driver.implicitly_wait(10)
            times = 4
            itens_pautas = None
            table_pautas: WebElement = self.wait.until(
                ec.all_of(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'pje-data-table[id="tabelaResultado"]',
                    ))
                ),
                (
                    ec.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        'table[name="Tabela de itens de pauta"]',
                    ))
                ),
            )[-1]

            with suppress(NoSuchElementException, TimeoutException):
                itens_pautas = table_pautas.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

            if itens_pautas:
                self.message = "Pautas encontradas!"
                self.type_log = "log"
                self.prt()

                times = 6

                for item in itens_pautas:
                    vara_name = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'span[class="ng-tns-c11-1 ng-star-inserted"]',
                    ).text
                    with suppress(StaleElementReferenceException):
                        item: WebElement = item
                        itens_tr = item.find_elements(By.TAG_NAME, "td")

                        appends = {
                            "INDICE": int(itens_tr[0].text),
                            "NUMERO_PROCESSO": itens_tr[3].find_element(By.TAG_NAME, "a").text.split(" ")[1],
                            "VARA": vara_name,
                            "HORARIO": itens_tr[1].text,
                            "TIPO": itens_tr[2].text,
                            "ATO": itens_tr[3].find_element(By.TAG_NAME, "a").text.split(" ")[0],
                            "PARTES": itens_tr[3]
                            .find_element(By.TAG_NAME, "span")
                            .find_element(By.TAG_NAME, "span")
                            .text,
                            "SALA": itens_tr[5].text,
                            "SITUACAO": itens_tr[6].text,
                        }

                        self.data_append[vara][current_date].append(appends)
                        self.message = f"Processo {appends['NUMERO_PROCESSO']} adicionado!"
                        self.type_log = "info"
                        self.prt()

                try:
                    btn_next = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Próxima página"]')

                    buttondisabled = btn_next.get_attribute("disabled")
                    if not buttondisabled:
                        btn_next.click()
                        self.get_pautas(current_date, vara)

                except Exception as e:
                    self.logger.exception("".join(traceback.format_exception_only(e)))
                    raise ExecutionError(e) from e

            elif not itens_pautas:
                times = 1

            sleep(times)

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception_only(e)))
            raise ExecutionError(e=e) from e
