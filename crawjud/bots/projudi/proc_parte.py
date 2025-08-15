"""Module: proc_parte.

Manage participant processing in the Projudi system by interacting with process lists and varas.
"""

import os
import time
import traceback
from contextlib import suppress
from typing import Self

from selenium.common.exceptions import (
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from crawjud.common.exceptions.bot import ExecutionError
from crawjud.interfaces.controllers.bots.systems.projudi import ProjudiBot


class ProcParte(ProjudiBot):
    """Handle participant processing in Projudi with detailed queue management and error handling.

    This class extends CrawJUD to retrieve process lists, store participant information,
    and manage queue execution for the Projudi system.
    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize a ProcParte instance with the specified parameters.

        Args:
            *args (tuple[str | int]): Positional arguments.
            **kwargs (dict[str, str | int]): Keyword arguments.

        Returns:
            Self: The initialized ProcParte instance.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the ProcParte instance and start authentication.

        Args:
            *args (tuple[str | int]): Positional arguments.
            **kwargs (dict[str, str | int]): Keyword arguments.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()
        self.data_append = []

    def execution(self) -> None:
        """Execute the main loop for participant processing continuously.

        Continuously process queues until stopping, while handling session expirations and errors.
        """
        self.graphicMode = "bar"
        while not self.isStoped:
            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                # TODO(Nicholas Silva): Criação de Exceptions
                # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
                old = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Manage the participant processing queue and handle varas search.

        Raises:
            ExecutionError: If process retrieval and queue execution fail.

        """
        try:
            for vara in self.varas:
                self.vara: str = vara
                search = self.search_bot()
                if search is True:
                    self.get_process_list()

                with suppress(Exception):
                    if self.driver.title.lower() == "a sessao expirou":
                        self.auth_bot()

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            old_message = None

            # check_window = any([isinstance(e, NoSuchWindowException), isinstance(e, MaxRetryError)])
            # if check_window:
            #     with suppress(Exception):
            #         self.driver_launch(message="Webdriver encerrado inesperadamente, reinicializando...")

            #         old_message = self.message

            #         self.auth_bot()

            if old_message is None:
                old_message = self.message
            message_error = str(e)

            self.type_log = "error"
            self.message_error = f"{message_error}. | Operação: {old_message}"
            self.prt()

            self.bot_data.update({"MOTIVO_ERRO": self.message_error})
            self.append_error(self.bot_data)

            self.message_error = None
            self.queue()

    def get_process_list(self) -> None:
        """Retrieve and process the list of processes from the web interface.

        Extracts process data, manages pagination, and stores the retrieved information.
        """
        try:
            table_processos = self.driver.find_element(
                By.CLASS_NAME,
                "resultTable",
            ).find_element(By.TAG_NAME, "tbody")

            list_processos = None
            next_page = None
            with suppress(NoSuchElementException):
                list_processos = table_processos.find_elements(
                    By.XPATH,
                    './/tr[contains(@class, "odd") or contains(@class, "even")]',
                )

            if list_processos and not self.isStoped:
                self.use_list_process(list_processos)

                with suppress(NoSuchElementException):
                    next_page = self.driver.find_element(
                        By.CLASS_NAME,
                        "navRight",
                    ).find_element(
                        By.XPATH,
                        self.elements.exception_arrow,
                    )

                self.type_log = "info"
                self.append_success(
                    self.data_append,
                    "Processos salvos na planilha!",
                    fileN=os.path.basename(self.path),
                )
                if next_page:
                    next_page.click()
                    self.get_process_list()

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def use_list_process(self, list_processos: list[WebElement]) -> None:
        """Extract and log details from each process element in the provided list.

        Args:
            list_processos (list[WebElement]): List of process web elements.

        """
        self.data_append.clear()
        for processo in list_processos:
            numero_processo = processo.find_elements(By.TAG_NAME, "td")[1].text

            numero = "".join(filter(str.isdigit, numero_processo))
            anoref = ""
            if numero:
                anoref = numero_processo.split(".")[1]

            try:
                polo_ativo = (
                    processo.find_elements(By.TAG_NAME, "td")[2]
                    .find_elements(By.TAG_NAME, "td")[1]
                    .text
                )
            except Exception:
                polo_ativo = "Não consta ou processo em sigilo"

            try:
                polo_passivo = processo.find_elements(By.TAG_NAME, "td")[7].text

            except Exception:
                polo_passivo = "Não consta ou processo em sigilo"

            try:
                juizo = processo.find_elements(By.TAG_NAME, "td")[9].text
            except Exception:
                juizo = "Não consta ou processo em sigilo"

            self.data_append.append(
                {
                    "NUMERO_PROCESSO": numero_processo,
                    "ANO_REFERENCIA": anoref,
                    "POLO_ATIVO": polo_ativo,
                    "POLO_PASSIVO": polo_passivo,
                    "JUIZO": juizo,
                },
            )
            self.row += 1
            self.message = f"Processo {numero_processo} salvo!"
            self.type_log = "success"
            self.prt()
