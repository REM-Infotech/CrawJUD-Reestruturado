"""Module: tjdft.

This module handles calculations related to the TJD-Federal Tribunal within the CrawJUD-Bots application.
"""

from __future__ import annotations

import base64
import os
from contextlib import suppress
from time import sleep
from typing import Self

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError

cookieaceito = []


class Tjdft(CrawJUD):
    """The Tjdft class extends CrawJUD to handle calculations for the TJD-Federal Tribunal.

    Attributes:
        cookieaceito (list): list to track accepted cookies.


    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """
        Initialize bot instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        return cls(*args, **kwargs)

    def execution(self) -> None:
        """Execute the main processing loop for calculations.

        Iterates over each entry in the data frame and processes it.
        Handles session expiration and error logger.

        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.is_stoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                self.tratamento_erros(exc=e)

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the calculation queue processing.

        Performs the calculation steps and finalizes the execution.

        Raises:
            ExecutionError: If an error occurs during queue processing.

        """
        try:
            self.get_calcular()
            self.info_numproc()
            self.info_requerente()
            self.info_requerido()
            self.info_jurosapartir()
            self.valores_devidos()
            self.acessorios()
            self.finalizar_execucao()

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def get_calcular(self) -> None:
        """Access the calculation page.

        This method navigates to the calculation URL and handles cookie acceptance if prompted.

        Raises:
            ExecutionError: If an error occurs while accessing the calculation page.

        """
        try:
            message = "Acessando Página de cálculo.."
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            self.driver.get(
                "https://www.tjdft.jus.br/servicos/atualizacao-monetaria-1/calculo"
            )

            check_cookies = None
            with suppress(TimeoutException):
                check_cookies = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            'div[class="alert text-center cookiealert show"]',
                        ),
                    ),
                )

            if check_cookies:
                sleep(2)

                aceitar_cookies_css = (
                    'button[class="btn btn-primary btn-sm acceptcookies"]'
                )
                aceitar_cookies: WebElement = self.driver.find_element(
                    By.CSS_SELECTOR, aceitar_cookies_css
                )
                aceitar_cookies.click()
                self.driver.switch_to.default_content()

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def info_numproc(self) -> None:
        """Inform the process number.

        This method fills in the process number in the calculation form.

        Raises:
            ExecutionError: If an error occurs while informing the process number.

        """
        try:
            sleep(2)
            message = "Informando numero do processo"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            css_input_numproc = 'input[id="num_processo"][name="num_processo"]'
            get_input_process: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_input_numproc)),
            )
            get_input_process.click()
            get_input_process.send_keys(self.bot_data.get("NUMERO_PROCESSO"))

            message = "numero do processo informado"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def info_requerente(self) -> None:
        """Inform the petitioner.

        This method fills in the petitioner's name in the calculation form.

        Raises:
            ExecutionError: If an error occurs while informing the petitioner.

        """
        try:
            sleep(2)
            css_name_requerente = 'input[name="requerente"][id="requerente"]'
            message = "Informando requerente"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            get_name_requerente: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    css_name_requerente,
                )),
            )
            get_name_requerente.click()
            get_name_requerente.send_keys(self.bot_data.get("REQUERENTE"))

            message = "Nome do requerente informado"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def info_requerido(self) -> None:
        """Inform the required party.

        This method fills in the required party's name in the calculation form.

        Raises:
            ExecutionError: If an error occurs while informing the required party.

        """
        try:
            sleep(2)
            css_name_requerido = 'input[name="requerido"][id="requerido"]'
            message = "Informado requerido"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            get_name_requerido: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_name_requerido)),
            )
            get_name_requerido.click()
            get_name_requerido.send_keys(self.bot_data.get("REQUERIDO"))

            message = "Nome do requerido informado"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def info_jurosapartir(self) -> None:
        """Inform the interest starting point.

        This method selects the interest starting point in the calculation form and informs the associated data.

        Raises:
            ExecutionError: If an error occurs while informing the interest starting point.

        """
        try:
            message = "Informando incidencia de juros e data de incidencia"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

            juros_partir = str(self.bot_data.get("JUROS_PARTIR")).upper()

            css_select_juros = 'select[id="juros_partir"][class="select-consultas"]'
            select = Select(
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        css_select_juros,
                    ))
                )
            )
            select.select_by_value(juros_partir)

            juros_percent = str(self.bot_data.get("JUROS_PERCENT", "1"))
            if juros_percent == "1":
                self.interact.click(
                    self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="juros_percent1"]'
                    )
                )

            elif juros_percent != "1":
                percent = juros_percent
                percent = f"{percent},00" if "," not in percent else percent

                self.interact.click(
                    self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="juros_percent2"]'
                    )
                )
                self.interact.send_key(
                    self.wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            'input[id="juros_percent_variavel"]',
                        )),
                    ),
                    percent,
                )

            if not juros_partir == "VENCIMENTO":
                css_data_incide = 'input[name="juros_data"][id="juros_data"]'
                self.interact.send_key(
                    self.driver.find_element(By.CSS_SELECTOR, css_data_incide),
                    self.bot_data.get("DATA_INCIDENCIA"),
                )

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def valores_devidos(self) -> None:
        """Inform the owed values.

        This method fills in the owed values and their dates in the calculation form.

        Raises:
            ExecutionError: If an error occurs while informing the owed values.

        """
        try:
            css_data_valor_devido = 'input[id="data-0"][name="parcela_data:list"]'
            message = "Informando data valor devido"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            data_valor_devido: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    css_data_valor_devido,
                )),
            )
            data_valor_devido.click()
            data_valor_devido.send_keys(self.bot_data.get("DATA_CALCULO"))

            sleep(2)
            css_valor_devido = 'input[id="valor-0"][name="parcela_valor:list"]'
            message = "Informando valor devido"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            valor_devido: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_valor_devido)),
            )
            valor_devido.click()

            valor = str(self.bot_data.get("VALOR_CALCULO"))
            valor = f"{valor},00" if "," not in valor else valor
            valor_devido.send_keys(valor)

            message = "valor devido informado"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def acessorios(self) -> None:
        """Inform accessory values like penalties and fees.

        This method handles the input of accessory financial details in the calculation form.

        """

        def multa_percentual() -> None | Exception:
            try:
                sleep(1)
                css_multa_percentual = (
                    'input[name="multa_percent"][id="multa_percent"]'
                )
                message = "Informando multa percentual"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

                if self.bot_data.get("MULTA_PERCENTUAL", None):
                    multa_percentual: WebElement = self.wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            css_multa_percentual,
                        )),
                    )
                    multa_percentual.click()

                    percent = str(self.bot_data.get("MULTA_PERCENTUAL"))
                    percent = f"{percent},00" if "," not in percent else percent
                    multa_percentual.send_keys(percent)

                if self.bot_data.get("MULTA_DATA", None):
                    multa_data = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="multa_data"]'
                    )
                    multa_valor = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="multa_valor"]'
                    )

                    valor = str(self.bot_data.get("MULTA_VALOR"))
                    valor = f"{valor},00" if "," not in valor else valor

                    self.interact.send_key(
                        multa_data, self.bot_data.get("MULTA_DATA")
                    )
                    self.interact.send_key(multa_valor, valor)

                message = "Multa informada"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

            except Exception as e:
                raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

        def honorario_sucumb() -> None | Exception:
            try:
                css_honorario_sucumb = (
                    'input[name="honor_sucumb_percent"][id="honor_sucumb_percent"]'
                )
                message = "Informando Honorários de Sucumbência"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

                disabled_state = ""

                if self.bot_data.get("HONORARIO_SUCUMB_PERCENT", None):
                    honorario_sucumb: WebElement = self.wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            css_honorario_sucumb,
                        )),
                    )
                    honorario_sucumb.click()
                    percent = str(self.bot_data.get("HONORARIO_SUCUMB_PERCENT"))
                    percent = f"{percent},00" if "," not in percent else percent

                    honorario_sucumb.send_keys(percent)
                    self.driver.execute_script(
                        f"document.querySelector('{css_honorario_sucumb}').blur()"
                    )
                    sleep(0.5)

                    disabled_state = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'input[id="honor_sucumb_data"]',
                    ).get_attribute("disabled")

                elif (
                    self.bot_data.get("HONORARIO_SUCUMB_DATA", None)
                    and disabled_state == ""
                ):
                    honor_sucumb_data = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_sucumb_data"]'
                    )
                    honor_sucumb_valor = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_sucumb_valor"]'
                    )
                    sucumb_juros_partir = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'input[id="honor_sucumb_juros_partir"]',
                    )

                    valor = str(self.bot_data.get("HONORARIO_SUCUMB_VALOR"))
                    valor = f"{valor},00" if "," not in valor else valor

                    self.interact.send_key(
                        honor_sucumb_data, self.bot_data.get("HONORARIO_SUCUMB_DATA")
                    )
                    self.interact.send_key(honor_sucumb_valor, valor)
                    self.interact.send_key(
                        sucumb_juros_partir,
                        self.bot_data.get("HONORARIO_SUCUMB_PARTIR"),
                    )

                message = "Percentual Honorários de Sucumbência informado"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

            except Exception as e:
                raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

        def percent_multa_475J() -> None:  # noqa: N802
            try:
                percent_multa_ = self.driver.find_element(
                    By.CSS_SELECTOR, 'input[id="multa475_exec_percent"]'
                )
                self.interact.send_key(
                    percent_multa_, self.bot_data.get("PERCENT_MULTA_475J")
                )

            except Exception as e:
                raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

        def honorario_cumprimento() -> None | Exception:
            try:
                css_honorario_exec = 'input[id="honor_exec_percent"]'
                message = "Informando Honorários de Cumprimento"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

                disabled_state = ""

                if self.bot_data.get("HONORARIO_CUMPRIMENTO_PERCENT", None):
                    honorario_exec: WebElement = self.wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            css_honorario_exec,
                        )),
                    )
                    honorario_exec.click()
                    percent = str(self.bot_data.get("HONORARIO_CUMPRIMENTO_PERCENT"))
                    percent = f"{percent},00" if "," not in percent else percent

                    honorario_exec.send_keys(percent)
                    self.driver.execute_script(
                        f"document.querySelector('{css_honorario_exec}').blur()"
                    )
                    sleep(0.5)

                    disabled_state = self.driver.find_element(
                        By.CSS_SELECTOR,
                        'input[id="honor_exec_data"]',
                    ).get_attribute("disabled")

                elif (
                    self.bot_data.get("HONORARIO_CUMPRIMENTO_DATA", None)
                    and disabled_state == ""
                ):
                    honor_exec_data = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_data"]'
                    )
                    honor_exec_valor = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_valor"]'
                    )
                    exec_juros_partir = self.driver.find_element(
                        By.CSS_SELECTOR, 'input[id="honor_exec_juros_partir"]'
                    )

                    valor = str(self.bot_data.get("HONORARIO_CUMPRIMENTO_VALOR"))
                    valor = f"{valor},00" if "," not in valor else valor

                    self.interact.send_key(
                        honor_exec_data,
                        self.bot_data.get("HONORARIO_CUMPRIMENTO_DATA"),
                    )
                    self.interact.send_key(honor_exec_valor, valor)
                    self.interact.send_key(
                        exec_juros_partir,
                        self.bot_data.get("HONORARIO_CUMPRIMENTO_PARTIR"),
                    )

                message = "Informado Honorários de Cumprimento"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

            except Exception as e:
                raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

        def custas() -> None | Exception:
            try:
                css_data_custas = 'input[id="custas-data-0"]'
                message = "Informando valor custas"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )
                data_custas: WebElement = self.driver.find_element(
                    By.CSS_SELECTOR, css_data_custas
                )
                data_custas.click()
                data_custas.send_keys(self.bot_data.get("CUSTAS_DATA"))

                sleep(2)
                css_custas_valor = 'input[id="custas-valor-0"]'
                message = "Informando valor devido"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )
                custas_valor: WebElement = self.driver.find_element(
                    By.CSS_SELECTOR, css_custas_valor
                )
                custas_valor.click()

                valor = str(self.bot_data.get("CUSTAS_VALOR"))
                valor = f"{valor},00" if "," not in valor else valor
                custas_valor.send_keys(valor)

                message = "Valor custas informado"
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

            except Exception as e:
                raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

        local_functions = list(locals().items())
        for name, func in local_functions:
            if not name == "self":
                for info in self.bot_data:
                    info = str(info)
                    if name.lower() in info.lower():
                        func()
                        break

    def finalizar_execucao(self) -> None:
        """Finalize the execution of the calculation.

        This method submits the calculation form, retrieves the calculated value, and saves the PDF receipt.

        Raises:
            ExecutionError: If an error occurs during finalization.

        """
        try:
            css_calcular = 'input[type="submit"][value="Calcular"][id="calcular"]'
            calcular = self.driver.find_element(By.CSS_SELECTOR, css_calcular)
            calcular.click()

            table_valorcalc: WebElement = self.wait.until(
                ec.presence_of_all_elements_located((
                    By.CSS_SELECTOR,
                    'table[class="grid listing"]',
                )),
            )[-1]
            row_valorcalc = table_valorcalc.find_element(
                By.TAG_NAME, "tbody"
            ).find_elements(By.TAG_NAME, "tr")[-1]
            valor_doc = float(
                row_valorcalc.find_elements(By.TAG_NAME, "td")[-1]
                .text.replace(".", "")
                .replace(",", "."),
            )

            print_options = PrintOptions()
            print_options.orientation = "portrait"

            pdf = self.driver.print_page(print_options)
            pdf_bytes = base64.b64decode(pdf)

            # Salva o PDF em um arquivo

            pdf_name = f"CALCULO - {self.bot_data.get('NUMERO_PROCESSO')} - {self.bot_data.get('REQUERENTE')} - {self.pid}.pdf"

            path_pdf = os.path.join(self.output_dir_path, pdf_name)
            with open(path_pdf, "wb") as file:  # noqa: FURB103
                file.write(pdf_bytes)

            data = [self.bot_data.get("NUMERO_PROCESSO"), pdf_name, valor_doc]

            self.append_success(data)

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e
