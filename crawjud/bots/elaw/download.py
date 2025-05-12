"""Module for managing document downloads from the ELAW system.

This module handles automated document downloads from the ELAW system, including file
management, renaming, and organization of downloaded content.

Classes:
    Download: Manages document downloads by extending the CrawJUD base class
"""

import os
import shutil
import traceback
from contextlib import suppress
from time import sleep
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError


class Download(CrawJUD):
    """The Download class extends CrawJUD to handle download tasks within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


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
        """Execute the download process.

        Raises:
            DownloadError: If an error occurs during execution.

        """
        frame = self.dataFrame()
        self.max_rows = len(frame)

        for pos, value in enumerate(frame):
            self.row = pos + 1
            self.bot_data = value
            if self.isStoped:
                break

            with suppress(Exception):
                if self.driver.title.lower() == "a sessao expirou":
                    self.auth_bot()

            try:
                self.queue()

            except Exception as e:
                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(message="Webdriver encerrado inesperadamente, reinicializando...")

                    old_message = self.message

                    self.auth_bot()

                if old_message is None:
                    old_message = self.message
                message_error = str(e)

                self.type_log = "error"
                self.message_error = f"{message_error}. | Operação: {old_message}"
                self.prt()

                self.bot_data.update({"MOTIVO_ERRO": self.message_error})
                self.append_error(self.bot_data)

                self.message_error = None

        self.finalize_execution()

    def queue(self) -> None:
        """Handle the download queue processing.

        Raises:
            DownloadQueueError: If an error occurs during queue processing.

        """
        try:
            search = self.search_bot()
            if search is True:
                self.message = "Processo encontrado!"
                self.type_log = "log"
                self.prt()
                self.buscar_doc()
                self.download_docs()
                self.message = "Arquivos salvos com sucesso!"
                self.append_success(
                    [self.bot_data.get("NUMERO_PROCESSO"), self.message, self.list_docs],
                    "Arquivos salvos com sucesso!",
                )

            elif not search:
                self.message = "Processo não encontrado!"
                self.type_log = "error"
                self.prt()
                self.append_error([self.bot_data.get("NUMERO_PROCESSO"), self.message])

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def buscar_doc(self) -> None:
        """Access the attachments page.

        Raises:
            DocumentSearchError: If an error occurs while accessing the page.

        """
        self.message = "Acessando página de anexos"
        self.type_log = "log"
        self.prt()
        anexosbutton: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.anexosbutton_css)),
        )
        anexosbutton.click()
        sleep(1.5)
        self.message = "Acessando tabela de documentos"
        self.type_log = "log"
        self.prt()

    def download_docs(self) -> None:
        """Download the documents.

        Raises:
            DocumentDownloadError: If an error occurs during downloading.

        """
        table_doc: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_table_doc)),
        )
        table_doc = table_doc.find_elements(By.TAG_NAME, "tr")

        if "," in self.bot_data.get("TERMOS"):
            termos = str(self.bot_data.get("TERMOS")).replace(", ", ",").replace(" ,", ",").split(",")

        elif "," not in self.bot_data.get("TERMOS"):
            termos = [str(self.bot_data.get("TERMOS"))]

        self.message = f'Buscando documentos que contenham "{self.bot_data.get("TERMOS").__str__().replace(",", ", ")}"'
        self.type_log = "log"
        self.prt()

        for item in table_doc:
            item: WebElement = item
            get_name_file = str(item.find_elements(By.TAG_NAME, "td")[3].find_element(By.TAG_NAME, "a").text)

            for termo in termos:
                if str(termo).lower() in get_name_file.lower():
                    sleep(1)

                    self.message = f'Arquivo com termo de busca "{termo}" encontrado!'
                    self.type_log = "log"
                    self.prt()

                    baixar = item.find_elements(By.TAG_NAME, "td")[13].find_element(
                        By.CSS_SELECTOR,
                        self.elements.botao_baixar,
                    )
                    baixar.click()

                    self.rename_doc(get_name_file)
                    self.message = "Arquivo baixado com sucesso!"
                    self.type_log = "info"
                    self.prt()

    def rename_doc(self, namefile: str) -> None:
        """Rename the downloaded document.

        Args:
            namefile (str): The new name for the file.

        Raises:
            DocumentRenameError: If an error occurs during renaming.

        """
        filedownloaded = False
        while True:
            for _, __, files in os.walk(os.path.join(self.output_dir_path)):
                for file in files:
                    if file.replace(" ", "") == namefile.replace(" ", ""):
                        filedownloaded = True
                        namefile = file
                        break

                if filedownloaded is True:
                    break

            old_file = os.path.join(self.output_dir_path, namefile)
            if os.path.exists(old_file):
                sleep(0.5)
                break

            sleep(0.01)

        filename_replaced = f"{self.pid} - {namefile.replace(' ', '')}"
        path_renamed = os.path.join(self.output_dir_path, filename_replaced)
        shutil.move(old_file, path_renamed)

        if not self.list_docs:
            self.list_docs = filename_replaced

        elif self.list_docs:
            self.list_docs = self.list_docs + "," + filename_replaced
