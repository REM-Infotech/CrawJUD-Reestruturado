"""Module for managing document downloads from the ELAW system.

This module handles automated document downloads from the ELAW system, including file
management, renaming, and organization of downloaded content.

Classes:
    Download: Manages document downloads by extending the CrawJUD base class
"""

import os
import shutil
from contextlib import suppress
from time import sleep
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.core import CrawJUD
from crawjud.exceptions.elaw import ElawError


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
        """Handle the download queue processing.

        Raises:
            DownloadQueueError: If an error occurs during queue processing.

        """
        try:
            search = self.search_bot.search(self.bot_data)
            if search is True:
                message = "Processo encontrado!"
                type_log = "log"
                self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
                self.buscar_doc()
                self.download_docs()
                message = "Arquivos salvos com sucesso!"
                self.append_success(
                    [self.bot_data.get("NUMERO_PROCESSO"), message, self.list_docs],
                    "Arquivos salvos com sucesso!",
                )

            elif not search:
                message = "Processo não encontrado!"
                type_log = "error"
                self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
                self.append_error([self.bot_data.get("NUMERO_PROCESSO"), message])

        except Exception as e:
            raise ElawError(exception=e, bot_execution_id=self.pid) from e

    def buscar_doc(self) -> None:
        """Access the attachments page.

        Raises:
            DocumentSearchError: If an error occurs while accessing the page.

        """
        message = "Acessando página de anexos"
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)
        anexosbutton: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.anexosbutton_css)),
        )
        anexosbutton.click()
        sleep(1.5)
        message = "Acessando tabela de documentos"
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

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

        message = f'Buscando documentos que contenham "{self.bot_data.get("TERMOS").__str__().replace(",", ", ")}"'
        type_log = "log"
        self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

        for item in table_doc:
            item: WebElement = item
            get_name_file = str(item.find_elements(By.TAG_NAME, "td")[3].find_element(By.TAG_NAME, "a").text)

            for termo in termos:
                if str(termo).lower() in get_name_file.lower():
                    sleep(1)

                    message = f'Arquivo com termo de busca "{termo}" encontrado!'
                    type_log = "log"
                    self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

                    baixar = item.find_elements(By.TAG_NAME, "td")[13].find_element(
                        By.CSS_SELECTOR,
                        self.elements.botao_baixar,
                    )
                    baixar.click()

                    self.rename_doc(get_name_file)
                    message = "Arquivo baixado com sucesso!"
                    type_log = "info"
                    self.prt.print_msg(message=message, pid=self.pid, row=self.row, type_log=type_log)

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
