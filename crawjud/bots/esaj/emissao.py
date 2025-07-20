"""Manage emission processes for CrawJUD-Bots.

This module executes the emission workflow by generating PDF documents,
navigating forms, and extracting barcodes following the ESaj requirements.
"""

import platform
import re
import time
from contextlib import suppress
from time import sleep
from typing import Self

import requests
from pypdf import PdfReader
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError, SaveError

type_docscss = {
    "custas_iniciais": {
        "cnpj": [
            'input[name="entity.flTipoPessoa"][value="J"]',
            'tr[id="campoNuCnpj"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CNPJ"]',
        ],
        "cpf": [
            'input[name="entity.flTipoPessoa"][value="F"]',
            'tr[id="campoNuCpf"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CPF"]',
        ],
    },
    "preparo ri": {
        "cnpj": [
            'input[name="entity.flTipoPessoa"][value="J"]',
            'tr[id="campoNuCnpj"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CNPJ"]',
        ],
        "cpf": [
            'input[name="entity.flTipoPessoa"][value="F"]',
            'tr[id="campoNuCpf"]',
            'input[name="entity.nuCpfCnpj"][rotulo="CPF"]',
        ],
    },
}


class Emissao(CrawJUD):
    """Perform emission tasks by generating docs and extracting PDF barcodes.

    This class executes the complete workflow for document emission. It
    initializes drivers, navigates pages, and processes PDF files.

    Attributes:
        count_doc (callable): Utility function to count document type.

    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize an Emissao instance with given parameters and settings.

        Args:
            *args (str|int): Variable length positional arguments.
            **kwargs (str|int): Arbitrary keyword arguments.

        Returns:
            Self: A new instance of Emissao.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize Emissao instance and configure authentication.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Side Effects:
            Authenticates bot and records start time for processing.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Perform emission processing iterating over data rows and handling errors.

        Iterates the data frame to run the emission workflow. Handles page timeouts,
        session renewals, and logs errors accordingly.
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
        """Queue emission tasks by generating docs and processing PDF barcodes.

        Executes the emission process by calling the appropriate method based on
        the guide type and then downloading the PDF.
        """
        try:
            custa = str(self.bot_data.get("TIPO_GUIA"))
            if custa.lower() == "custas iniciais":
                self.tipodoc = custa
                self.custas_iniciais()

            elif custa.lower() == "preparo ri":
                custa = "Custas Preparo"
                self.tipodoc = custa
                self.preparo_ri()

            self.downloadpdf(self.generate_doc())
            self.append_success(self.get_barcode())

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def custas_iniciais(self) -> None:
        """Process initial costs: navigate to the correct URL and fill form fields.

        Fills necessary fields for calculating initial costs using data from the bot.
        """
        url_custas_ini = "".join(
            (
                "https://consultasaj.tjam.jus.br/ccpweb/iniciarCalculoDeCustas.do?",
                "cdTipoCusta=7&flTipoCusta=0&&cdServicoCalculoCusta=690003",
            ),
        )

        self.driver.get(url_custas_ini)

        message = "Informando foro"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        set_foro: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.ome_foro)),
        )
        set_foro.send_keys(self.bot_data.get("FORO"))

        set_classe = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.tree_selection
        )
        set_classe.send_keys(self.bot_data.get("CLASSE"))

        semprecível = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.civil_selector
        )
        semprecível.click()

        val_acao = self.driver.find_element(By.CSS_SELECTOR, self.elements.valor_acao)
        val_acao.send_keys(self.bot_data.get("VALOR_CAUSA"))

        nameinteressado = self.driver.find_element(
            By.CSS_SELECTOR, 'input[name="entity.nmInteressado"]'
        )
        nameinteressado.send_keys(self.bot_data.get("NOME_INTERESSADO"))

        elements: list = type_docscss.get(self.bot_data.get("TIPO_GUIA")).get(
            self.count_doc(self.bot_data.get("CPF_CNPJ")),
        )
        set_doc = self.driver.find_element(By.CSS_SELECTOR, elements[0])
        set_doc.click()
        sleep(0.5)
        setcpf_cnpj = self.driver.find_element(
            By.CSS_SELECTOR, elements[1]
        ).find_element(By.CSS_SELECTOR, elements[2])
        sleep(0.5)
        setcpf_cnpj.send_keys(self.bot_data.get("CPF_CNPJ"))

        avançar = self.driver.find_element(
            By.CSS_SELECTOR, self.elements.botao_avancar
        )
        avançar.click()

        self.valor_doc = ""
        with suppress(TimeoutException):
            css_val_doc = self.elements.css_val_doc_custas_ini
            self.valor_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_val_doc)),
            ).text

    def preparo_ri(self) -> None:
        """Process RI preparation: navigate portals and submit form data appropriately.

        Depending on the portal (ESaj or Projudi), fills the corresponding form fields.
        """
        portal = self.bot_data.get("PORTAL", "não informado")
        if str(portal).lower() == "esaj":
            self.driver.get(self.elements.url_preparo_esaj)

        elif str(portal).lower() == "projudi":
            self.driver.get(self.elements.url_preparo_projudi)

            set_foro: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.nome_foro,
                )),
            )
            set_foro.send_keys(self.bot_data.get("FORO"))

            val_acao = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.valor_acao
            )
            val_acao.send_keys(self.bot_data.get("VALOR_CAUSA"))

            nameinteressado = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.interessado
            )
            nameinteressado.send_keys(self.bot_data.get("NOME_INTERESSADO"))

            elements: list = type_docscss.get(self.bot_data.get("TIPO_GUIA")).get(
                self.count_doc(self.bot_data.get("CPF_CNPJ")),
            )

            set_doc = self.driver.find_element(By.CSS_SELECTOR, elements[0])
            set_doc.click()
            sleep(0.5)
            setcpf_cnpj = self.driver.find_element(
                By.CSS_SELECTOR, elements[1]
            ).find_element(
                By.CSS_SELECTOR,
                elements[2],
            )
            sleep(0.5)
            setcpf_cnpj.send_keys(self.bot_data.get("CPF_CNPJ"))

            avançar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_avancar
            )
            avançar.click()

            sleep(1)
            set_RI: WebElement = self.wait.until(  # noqa: N806
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.check))
            )
            set_RI.click()

            sleep(1)
            last_avançar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_avancar_dois
            )
            last_avançar.click()

            sleep(1)
            css_val_doc = "body > table:nth-child(4) > tbody > tr > td > table:nth-child(10) > tbody > tr:nth-child(3) > td:nth-child(3) > strong"  # noqa: E501
            self.valor_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_val_doc)),
            ).text

        elif portal == "não informado":
            raise SaveError(
                message="Informar portal do processo na planilha (PROJUDI ou ESAJ)",
                bot_execution_id=self.pid,
            )

    def renajud(self) -> None:
        """Implement Renajud emission process navigation and actions when needed.

        Note:
            Functionality is pending implementation.

        """

    def sisbajud(self) -> None:
        """Implement Sisbajud emission process functionality when required.

        Note:
            Future implementation is needed.

        """

    def custas_postais(self) -> None:
        """Implement postal costs process handling if further processing is required.

        Note:
            Implementation is pending.

        """

    def generate_doc(self) -> str:
        """Generate a PDF document URL by opening a new browser tab and switching context.

        Returns:
            str: The validated URL for the generated PDF document.

        Raises:
            ExecutionError: If the generated PDF contains an error message.

        """
        self.original_window = original_window = self.driver.current_window_handle
        generatepdf: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.boleto)),
        )
        onclick_value = generatepdf.get_attribute("onclick")
        url_start = onclick_value.find("'") + 1
        url_end = onclick_value.find("'", url_start)
        url = onclick_value[url_start:url_end]
        sleep(0.5)
        self.driver.switch_to.new_window("tab")
        self.driver.get(f"https://consultasaj.tjam.jus.br{url}")
        sleep(2)

        # Checar se não ocorreu o erro "Boleto inexistente"
        check = None
        with suppress(TimeoutException):
            check: WebElement = (
                WebDriverWait(self.driver, 3)
                .until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.mensagem_retorno,
                    ))
                )
                .text
            )

        if check:
            self.driver.close()
            sleep(0.7)
            self.driver.switch_to.window(original_window)
            raise SaveError(
                message="Esaj não gerou a guia", bot_execution_id=self.pid
            )

        if not check:
            return f"https://consultasaj.tjam.jus.br{url}"

    def downloadpdf(self, link_pdf: str) -> None:
        """Download and store the PDF file from the provided URL to a local directory.

        Args:
            link_pdf (str): URL of the PDF to download.

        Side Effects:
            Saves the PDF to disk and switches browser windows.

        """
        response = requests.get(link_pdf, timeout=60)

        self.nomearquivo = f"{self.tipodoc} - {self.bot_data.get('NUMERO_PROCESSO')} - {self.nomeparte} - {self.pid}.pdf"

        if platform.system() == "Windows":
            self.path_pdf = path_pdf = f"{self.output_dir_path}\\{self.nomearquivo}"

        elif platform.system() == "Linux":
            self.path_pdf = path_pdf = f"{self.output_dir_path}/{self.nomearquivo}"

        with open(path_pdf, "wb") as file:
            file.write(response.content)

        self.driver.close()
        sleep(0.7)
        self.driver.switch_to.window(self.original_window)
        message = (
            f"Boleto Nº{self.bot_data.get('NUMERO_PROCESSO')} emitido com sucesso!"
        )
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def get_barcode(self) -> None:
        """Extract and return the barcode from the downloaded PDF by matching a regex.

        Returns:
            list: Emission details including process number, doc type, value, and barcode.

        Raises:
            ExecutionError: If barcode extraction fails.

        """
        try:
            message = "Extraindo código de barras"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

            sleep(2)
            # Inicialize uma lista para armazenar os números encontrados
            bar_code = ""
            numeros_encontrados = []

            # Expressão regular para encontrar números nesse formato
            pattern = r"\b\d{5}\.\d{5}\s*\d{5}\.\d{6}\s*\d{5}\.\d{6}\s*\d\s*\d{14}\b"

            pdf_file = self.path_pdf
            read = PdfReader(pdf_file)

            # Read PDF
            for page in read.pages:
                text = page.extract_text()

                # Use a expressão regular para encontrar números
                numeros = re.findall(pattern, text)

                # Adicione os números encontrados à lista
                numeros_encontrados.extend(numeros)

            # Imprima os números encontrados
            for numero in numeros_encontrados:
                bar_code = numero.replace("  ", "")
                bar_code = bar_code.replace(" ", "")
                bar_code = bar_code.replace(".", " ")
                numero = numero.split("  ")
                numero = numero[2].split(".")

            return [
                self.bot_data.get("NUMERO_PROCESSO"),
                self.tipodoc,
                self.valor_doc,
                self.data_lancamento,
                "guias",
                "JEC",
                "SENTENÇA",
                bar_code,
                self.nomearquivo,
            ]

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e
