"""Module for tracking and recording process progress in the ELAW system.

This module handles the creation and management of process progress records within the ELAW
system. It automates the recording of progress updates and related documentation.

Classes:
    Andamentos: Manages process progress by extending the CrawJUD base class
"""

from contextlib import suppress
from time import sleep
from typing import Self

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import SaveError
from crawjud.exceptions.elaw import ElawError


class Andamentos(CrawJUD):
    """The Andamentos class manages the andamento tracking bot."""

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
        """Execute the main processing loop for andamentos.

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
        """Handle the andamento queue processing.

        Attempts to perform the andamento operations and handles cases where the process is not found.

        Raises:
            ExecutionError: If an error occurs during queue processing.

        """
        try:
            search = self.search_bot()
            if search is True:
                btn_newmove = self.elements.botao_andamento
                new_move: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, btn_newmove)))
                new_move.click()

                self.info_data()
                self.info_ocorrencia()
                self.info_observacao()

                if self.bot_data.get("ANEXOS", None):
                    self.add_anexo()

                self.save_andamento()

            elif search is not True:
                message = "Processo não encontrado!"
                type_log = "error"
                self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
                self.append_error([self.bot_data.get("NUMERO_PROCESSO"), message])

        except Exception as e:
            raise ElawError(exception=e, bot_execution_id=self.pid) from e

    def info_data(self) -> None:
        """Inform the date of the andamento.

        This method fills in the date field in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the date.

        """
        try:
            message = "Informando data"
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
            css_Data = self.elements.input_data  # noqa: N806
            campo_data: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, css_Data)))
            campo_data.click()
            campo_data.send_keys(Keys.CONTROL, "a")
            sleep(0.5)
            campo_data.send_keys(Keys.BACKSPACE)
            self.interact.send_key(campo_data, self.bot_data.get("DATA"))
            campo_data.send_keys(Keys.TAB)

            self.interact.sleep_load('div[id="j_id_34"]')

        except Exception as e:
            raise ElawError(exception=e, bot_execution_id=self.pid) from e

    def info_ocorrencia(self) -> None:
        """Inform the occurrence details of the andamento.

        This method fills in the occurrence details in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the occurrence.

        """
        try:
            message = "Informando ocorrência"
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

            ocorrencia = self.driver.find_element(By.CSS_SELECTOR, self.elements.inpt_ocorrencia)
            text_andamento = str(self.bot_data.get("OCORRENCIA")).replace("\t", "").replace("\n", "")

            self.interact.send_key(ocorrencia, text_andamento)

        except Exception as e:
            raise ElawError(exception=e, bot_execution_id=self.pid) from e

    def info_observacao(self) -> None:
        """Inform the observation details of the andamento.

        This method fills in the observation details in the andamento form.

        Raises:
            ExecutionError: If an error occurs while informing the observation.

        """
        try:
            message = "Informando observação"
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

            observacao = self.driver.find_element(By.CSS_SELECTOR, self.elements.inpt_obs)
            text_andamento = str(self.bot_data.get("OBSERVACAO")).replace("\t", "").replace("\n", "")

            self.interact.send_key(observacao, text_andamento)

        except Exception as e:
            raise ElawError(exception=e, bot_execution_id=self.pid) from e

    def add_anexo(self) -> None:
        """Add attachments to the andamento.

        This method handles the addition of attachments to the andamento form.

        Raises:
            NotImplementedError: If the method is not yet implemented.

        """

    def save_andamento(self) -> None:
        """Save the andamento details.

        This method clicks the save button to persist the andamento data and verifies the save operation.

        Raises:
            ExecutionError: If the save operation fails or cannot be validated.

        """
        try:
            message = "Salvando andamento..."
            type_log = "log"
            self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
            sleep(1)
            self.link = self.driver.current_url
            save_button = self.driver.find_element(By.ID, self.elements.botao_salvar_andamento)
            save_button.click()

        except Exception as e:
            raise SaveError(message="Não foi possivel salvar andamento", exception=e, bot_execution_id=self.pid) from e

        try:
            check_save: WebElement = WebDriverWait(self.driver, 10).until(
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
            )
            if check_save:
                sleep(3)

                self.append_success([self.numproc, "Andamento salvo com sucesso!", ""], "Andamento salvo com sucesso!")

        except Exception as e:
            raise SaveError(
                message="Aviso: não foi possivel validar salvamento de andamento",
                exception=e,
                bot_execution_id=self.pid,
            ) from e
