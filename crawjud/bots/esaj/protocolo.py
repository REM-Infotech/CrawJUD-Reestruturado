"""Module: protocolo.

This module manages protocol operations in the ESaj system using the CrawJUD framework.
"""

import os
import shutil
import unicodedata
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import (
    CadastroParteError,
    ExecutionError,
    FileError,
    SaveError,
)


class Protocolo(CrawJUD):
    """Class Protocolo.

    Manage protocol operations in the ESaj system via CrawJUD.

    Attributes:
        start_time (float): Time when the protocol process starts.
        bot_data (dict): Data for the current protocol entry.


    Methods:
        initialize: Create and return a new Protocolo instance.
        execution: Run protocol processing loop.
        queue: Execute protocoling steps with error handling.
        init_protocolo: Start the petition process.
        set_tipo_protocolo: Select and input the protocol type.
        set_subtipo_protocolo: Select and input the protocol subtype.
        set_petition_file: Attach the petition document.
        vincular_parte: Link a party to the petition.
        finish_petition: Finalize petition process.
        get_confirm_protocol: Confirm protocol and process receipt.

    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize a new Protocolo instance.

        Args:
            *args (str | int): Variable number of string or int arguments.
            **kwargs (str | int): Arbitrary keyword arguments.

        Returns:
            Self: A new Protocolo instance.

        # Inline: Delegate initialization to the class constructor.

        """
        return cls(*args, **kwargs)

    def execution(self) -> None:
        """Execute protocol processing on each row.

        Iterates over protocol rows and handles session renewals and errors.

        Raises:
            ExecutionError: If an error occurs during protocol processing.

        # Inline: Loop through dataFrame and process protocols.

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
        """Queue protocol steps.

        Executes the sequence of protocol operations and handles exceptions accordingly.

        Raises:
            ExecutionError: If any protocol step fails.

        # Inline: Wrap steps in try/except to handle ExecutionError.

        """
        try:
            self.search_bot.search()
            self.init_protocolo()
            self.set_tipo_protocolo()
            self.set_subtipo_protocolo()
            self.set_petition_file()
            self.vincular_parte()
            self.finish_petition()
            data = self.get_confirm_protocol()
            self.append_success(data, message=data[1])

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def init_protocolo(self) -> None:
        """Initialize petition process.

        Navigates to the petition section and starts the protocol procedure.

        Raises:
            ExecutionError: If unable to initialize petitioning.

        # Inline: Attempt primary button click; fallback to alternative.

        """
        try:
            try:
                self.prt.print_log(
                    "log", "Processo encontrado! Inicializando peticionamento..."
                )
                button_peticionamento: WebElement = WebDriverWait(
                    self.driver, 10
                ).until(
                    ec.element_to_be_clickable((By.ID, "pbPeticionar")),
                )
                link = button_peticionamento.get_attribute("onclick").split("'")[1]
                self.driver.execute_script(f"return window.location.href = '{link}';")
                sleep(5)

            except Exception:
                button_enterproc: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        "#processoSelecionado",
                    )),
                )
                button_enterproc.click()

                enterproc: WebElement = WebDriverWait(self.driver, 5).until(
                    ec.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        "#botaoEnviarIncidente",
                    )),
                )
                enterproc.click()
                button_peticionamento: WebElement = WebDriverWait(
                    self.driver, 10
                ).until(
                    ec.element_to_be_clickable((By.ID, "pbPeticionar")),
                )
                link = button_peticionamento.get_attribute("onclick").split("'")[1]
                self.driver.execute_script(f"return window.location.href = '{link}';")

        except Exception as e:
            raise ExecutionError(
                message="Erro ao inicializar peticionamento",
                bot_execution_id=self.pid,
                exception=e,
            ) from None

    def set_tipo_protocolo(self) -> None:
        """Set protocol type.

        Selects and inputs the protocol type using provided bot data.

        Raises:
            ExecutionError: If there is an error while setting the protocol type.

        # Inline: Wait for element load and simulate typing.

        """
        try:
            self.interact.sleep_load('div[id="loadFeedback"]')
            self.prt.print_log("log", "Informando tipo de peticionamento")
            button_classification: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.ID,
                    self.elements.editar_classificacao,
                )),
            )
            self.interact.click(button_classification)

            select_tipo_peticao: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.selecionar_classe,
                )),
            )
            select_tipo_peticao = select_tipo_peticao.find_element(
                By.CSS_SELECTOR, self.elements.toggle
            )
            self.interact.click(select_tipo_peticao)

            input_tipo_peticao: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.input_classe,
                )),
            )
            self.interact.send_key(
                input_tipo_peticao, self.bot_data.get("TIPO_PROTOCOLO")
            )
            sleep(1.5)
            self.interact.send_key(input_tipo_peticao, Keys.ENTER)

        except Exception as e:
            raise ExecutionError(
                message="Erro ao informar tipo de protocolo",
                bot_execution_id=self.pid,
                exception=e,
            ) from e

    def set_subtipo_protocolo(self) -> None:
        """Set protocol subtype.

        Selects and inputs the protocol subtype based on bot data.

        Raises:
            ExecutionError: If failing to set the protocol subtype.

        # Inline: Click toggle and select subgroup.

        """
        try:
            self.prt.print_log("log", "Informando subtipo de peticionamento")
            select_categoria_peticao: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.select_categoria,
                )),
            )
            select_categoria_peticao = select_categoria_peticao.find_element(
                By.CSS_SELECTOR, self.elements.toggle
            )
            self.interact.click(select_categoria_peticao)

            input_categoria_peticao: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.input_categoria,
                )),
            )
            self.interact.send_key(
                input_categoria_peticao, self.bot_data.get("SUBTIPO_PROTOCOLO")
            )

            input_categoria_peticao_option: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    self.elements.selecionar_grupo,
                )),
            )
            input_categoria_peticao_option.click()
            sleep(1)

        except Exception as e:
            raise ExecutionError(
                exception=e,
                message="Erro ao informar subtipo de protocolo",
                bot_execution_id=self.pid,
            ) from e

    def set_petition_file(self) -> None:
        """Attach petition file.

        Uploads the petition document and verifies its successful submission.

        Raises:
            ExecutionError: If the petition file fails to upload.

        # Inline: Normalize file path and send file key.

        """
        try:
            self.prt.print_log("log", "Anexando petição")
            input_file: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.input_documento,
                )),
            )
            sleep(2)

            path_file = Path(self.path_args).parent.resolve().__str__()
            file = os.path.join(path_file, self.bot_data.get("PETICAO_PRINCIPAL"))

            file = file.replace(" ", "")
            if "_" in file:
                file = file.replace("_", "")

            file = unicodedata.normalize("NFKD", file)
            file = "".join([c for c in file if not unicodedata.combining(c)])

            input_file.send_keys(file)

            file_uploaded = ""
            with suppress(TimeoutException):
                file_uploaded: WebElement = WebDriverWait(self.driver, 25).until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        self.elements.documento,
                    )),
                )

            if file_uploaded == "":
                raise FileError(
                    message="Erro ao enviar petição", bot_execution_id=self.pid
                )

            self.prt.print_log("log", "Petição do processo anexada com sucesso")

        except Exception as e:
            raise FileError(
                message="Erro ao enviar petição", bot_execution_id=self.pid
            ) from e

    def vincular_parte(self) -> None:
        """Link party to petition.

        Associates the specified party with the petition based on bot data.

        Raises:
            ExecutionError: If the party cannot be linked.

        # Inline: Compare party names and click the inclusion button.

        """
        try:
            parte_peticao = self.bot_data.get("PARTE_PETICIONANTE").__str__().lower()
            self.prt.print_log("log", "Vinculando parte a petição...")
            partes: WebElement = self.wait.until(
                ec.presence_of_all_elements_located((
                    By.CSS_SELECTOR,
                    self.elements.processo_view,
                )),
            )
            if partes:
                for parte in partes:
                    parte: WebElement = parte
                    parte_name = parte.find_element(
                        By.CSS_SELECTOR, self.elements.nome
                    ).text.lower()
                    if parte_name == parte_peticao:
                        sleep(3)

                        incluir_button = None
                        with suppress(NoSuchElementException):
                            incluir_button = parte.find_element(
                                By.CSS_SELECTOR, self.elements.botao_incluir_peticao
                            )

                        if not incluir_button:
                            with suppress(NoSuchElementException):
                                incluir_button = parte.find_element(
                                    By.CSS_SELECTOR,
                                    self.elements.botao_incluir_partecontraria,
                                )

                        incluir_button.click()

                        self.prt.print_log("log", "Vinculando cliente à petição...")
                        sleep(0.3)
                        break

                    if parte_name != parte_peticao:
                        partes = self.driver.find_elements(
                            By.CSS_SELECTOR, self.elements.parte_view
                        )
                        for parte in partes:
                            parte_name = parte.find_element(
                                By.CSS_SELECTOR, self.elements.nome
                            ).text.lower()
                            if parte_name == parte_peticao.lower():
                                self.prt.print_log(
                                    "log",
                                    "Parte já vinculada, finalizando peticionamento...",
                                )
                                sleep(0.3)
                                break

            elif not partes:
                raise CadastroParteError(
                    message="Não foi possivel vincular parte a petição",
                    bot_execution_id=self.pid,
                )

        except Exception as e:
            raise ExecutionError(
                exception=e,
                bot_execution_id=self.pid,
            ) from e

    def finish_petition(self) -> None:
        """Finalize petition process.

        Completes the petition process by confirming and saving process details.

        # Inline: Click finish and then confirm the petition.
        """
        self.prt.print_log("log", "Finalizando...")

        finish_button = self.driver.find_element(
            By.XPATH, self.elements.botao_protocolar
        )
        sleep(1)
        finish_button.click()
        sleep(5)

        confirm_button: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.botao_confirmar,
            )),
        )
        confirm_button.click()

    def get_confirm_protocol(self) -> list:
        """Confirm protocol and process receipt.

        Waits for confirmation, captures a screenshot, and moves the receipt file.

        Returns:
            list: Contains process number, success message, and receipt filename.

        Raises:
            ExecutionError: If unable to confirm protocol.

        # Inline: Use WebDriverWait to ensure receipt element is present.

        """
        try:
            getlinkrecibo: WebElement = WebDriverWait(self.driver, 60).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.botao_recibo,
                )),
            )

            sleep(3)

            name_recibo = f"Recibo Protocolo - {self.bot_data.get('NUMERO_PROCESSO')} - PID {self.pid}.pdf"
            self.driver.get_screenshot_as_file(
                f"{self.output_dir_path}/{name_recibo.replace('.pdf', '.png')}"
            )

            getlinkrecibo.click()

            path = os.path.join(self.output_dir_path, name_recibo)
            pathpdf = os.path.join(
                Path(self.path_args).parent.resolve(), "recibo.pdf"
            )

            while True:
                if os.path.exists(pathpdf):
                    sleep(0.5)
                    break

            shutil.move(pathpdf, path)
            return [
                self.bot_data.get("NUMERO_PROCESSO"),
                f"Processo nº{self.bot_data.get('NUMERO_PROCESSO')} protocolado com sucesso!",
                name_recibo,
            ]

        except Exception as e:
            raise SaveError(
                message="Erro ao confirmar protocolo",
                exception=e,
                bot_execution_id=self.pid,
            ) from e
