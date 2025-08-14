"""Automação para extração e processamento de pautas judiciais no PJe.

Este módulo contém a classe e funções responsáveis por buscar, processar e registrar
pautas de audiências judiciais utilizando Selenium, além de tratar erros e gerar logs
durante a execução automatizada das tarefas.
"""

from contextlib import suppress
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.controllers.bots.systems.pje import PjeBot as ClassBot
from crawjud_app.bots.pje.resources._varas_dict import varas as varas_pje
from crawjud_app.custom.task import ContextTask
from crawjud_app.decorators import shared_task

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


@shared_task(name="pje.pauta", bind=True, base=ContextTask)
class Pauta(ContextTask, ClassBot):
    """Implemente a automação para buscar e processar pautas de audiências judiciais.

    Esta classe executa tarefas automatizadas para extração de pautas de audiências
    judiciais, utilizando Selenium para navegação e coleta de dados em sistemas PJe.
    """

    def execution(self) -> None:
        """Execute o fluxo principal para buscar e processar pautas de audiências.

        Args:
            self (Pauta): Instância da classe Pauta.

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

            message = "Buscando pautas na vara: " + vara_name
            type_log = "log"
            self.prt.print_msg(
                message=message,
                pid=self.pid,
                row=self.row,
                type_log=type_log,
            )

            if self.is_stoped:
                break

            if varas:
                vara_name = varas.get(vara)

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue(vara)

            except ExecutionError as e:
                self.tratamento_erros(exc=e)

        self.finalize_execution()

    def queue(self, vara: str) -> None:
        """Realize a busca e o processamento das pautas para uma vara específica.

        Args:
            vara (str): Nome ou identificador da vara a ser processada.

        Raises:
            ExecutionError: Caso ocorra erro durante a execução
                da busca ou processamento.

        """
        try:
            self.current_date = self.data_inicio
            while self.current_date <= self.data_fim:
                current_date_ = self.current_date.strftime("%d/%m/%Y")
                message = f"Buscando pautas na data {current_date_}"
                type_log = "log"
                self.prt.print_msg(
                    message=message,
                    pid=self.pid,
                    row=self.row,
                    type_log=type_log,
                )

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
                    file_name_ = (
                        f"{vara} - {date.replace('-', '.')} - {self.pid}.xlsx"
                    )
                    self.append_success(data=data_append, _file_name=file_name_)

                self.current_date += timedelta(days=1)

            data_append = self.group_date_all(self.data_append)
            file_name_ = Path(self.planilha_sucesso).name
            if len(data_append) > 0:
                self.append_success(
                    data=[data_append],
                    _file_name=file_name_,
                    message="Dados extraídos com sucesso!",
                )

            elif len(data_append) == 0:
                message = "Nenhuma pauta encontrada"
                type_log = "error"
                self.prt.print_msg(
                    message=message,
                    pid=self.pid,
                    row=self.row,
                    type_log=type_log,
                )

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def get_pautas(self, current_date: type[datetime], vara: str) -> None:
        """Busque e processe as pautas de audiências para uma data e vara específicas.

        Args:
            current_date (type[datetime]): Data da pauta a ser processada.
            vara (str): Nome ou identificador da vara.

        Raises:
            ExecutionError: Caso ocorra erro durante a busca
                ou processamento das pautas.

        """
        try:
            self.driver.implicitly_wait(10)
            times = 4
            itens_pautas: WebElement = None
            table_pautas: WebElement = self.wait.until(
                ec.all_of(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        'pje-data-table[id="tabelaResultado"]',
                    )),
                ),
                (
                    ec.visibility_of_element_located((
                        By.CSS_SELECTOR,
                        'table[name="Tabela de itens de pauta"]',
                    ))
                ),
            )[-1]

            with suppress(NoSuchElementException, TimeoutException):
                itens_pautas = table_pautas.find_element(
                    By.TAG_NAME,
                    "tbody",
                ).find_elements(By.TAG_NAME, "tr")

            if itens_pautas:
                message = "Pautas encontradas!"
                type_log = "log"
                self.prt.print_msg(
                    message=message,
                    pid=self.pid,
                    row=self.row,
                    type_log=type_log,
                )

                times = 6

                for item in itens_pautas:
                    vara_name = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'span[class="ng-tns-c11-1 ng-star-inserted"]',
                    ).text
                    with suppress(StaleElementReferenceException):
                        itens_tr = item.find_elements(By.TAG_NAME, "td")

                        appends = {
                            "INDICE": int(itens_tr[0].text),
                            "NUMERO_PROCESSO": itens_tr[3]
                            .find_element(By.TAG_NAME, "a")
                            .text.split(" ")[1],
                            "VARA": vara_name,
                            "HORARIO": itens_tr[1].text,
                            "TIPO": itens_tr[2].text,
                            "ATO": itens_tr[3]
                            .find_element(By.TAG_NAME, "a")
                            .text.split(" ")[0],
                            "PARTES": itens_tr[3]
                            .find_element(By.TAG_NAME, "span")
                            .find_element(By.TAG_NAME, "span")
                            .text,
                            "SALA": itens_tr[5].text,
                            "SITUACAO": itens_tr[6].text,
                        }

                        self.data_append[vara][current_date].append(appends)
                        message = f"Processo {appends['NUMERO_PROCESSO']} adicionado!"
                        type_log = "info"
                        self.prt.print_msg(
                            message=message,
                            pid=self.pid,
                            row=self.row,
                            type_log=type_log,
                        )

                try:
                    btn_next = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'button[aria-label="Próxima página"]',
                    )

                    buttondisabled = btn_next.get_attribute("disabled")
                    if not buttondisabled:
                        btn_next.click()
                        self.get_pautas(current_date, vara)

                except Exception as e:
                    # TODO(Nicholas Silva): Criação de Exceptions
                    # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
                    raise ExecutionError(
                        exception=e,
                        bot_execution_id=self.pid,
                    ) from e

            elif not itens_pautas:
                times = 1

            sleep(times)

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e
