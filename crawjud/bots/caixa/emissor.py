"""Manage deposit documents and operations in the Caixa system for CrawJUD-Bots effectively.

Provide a set of methods to handle site navigation, form filling, document creation,
and PDF processing in compliance with Google/PEP 257 docstring standards.
"""

import os
import re
import shutil
import time
from contextlib import suppress
from time import sleep
from typing import Self

from pypdf import PdfReader
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError


class Emissor(CrawJUD):
    """Manage creation and processing of judicial deposit documents using the Emissor bot fully.

    Offer a range of functionalities to access deposit pages, handle login flows,
    generate PDFs, and extract relevant data for deposit operations.
    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Create a new Emissor instance for handling deposit operations systematically.

        Args:
            *args (str|int): Positional parameters for setup and environment details.
            **kwargs (str|int): Configuration and keyword parameters for initialization.

        Returns:
            Emissor: Newly instantiated Emissor bot ready for execution.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize Emissor with environment variables, login, and performance tracking.

        Args:
            *args (str|int): Positional parameters for environment setup.
            **kwargs (str|int): Keyword arguments used for custom configuration.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()  # Tracks the bot's start time

    def execution(self) -> None:
        """Run the main operation loop and handle each DataFrame row comprehensively.

        Iterate through the DataFrame while checking session validity, capturing
        errors, and resuming operations as required.
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
        """Orchestrate the entire deposit emission procedure and record success or error.

        Execute steps like site navigation, deposit data input, PDF creation,
        and data extraction in a single call.
        """
        try:
            nameboleto = None
            self.get_site()
            self.locale_proc()
            self.proc_nattribut()
            self.dados_partes()
            self.info_deposito()
            self.make_doc()
            nameboleto = self.rename_pdf()
            data = self.get_val_doc_and_codebar(nameboleto)
            self.append_success(data)

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def get_site(self) -> None:
        """Access deposit site, solve CAPTCHA, and load required deposit interface.

        Navigate to the deposit page, handle CAPTCHA resolution, and select
        deposit type for further processing.
        """
        message = "Acessando página de emissão"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.driver.get(
            "https://depositojudicial.caixa.gov.br/sigsj_internet/depositos-judiciais/justica-estadual/"
        )
        sleep(0.5)
        list_opt: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'select[id="j_id5:filtroView:j_id6:tpDeposito"]',
            )),
        )
        sleep(0.5)
        list_options = list_opt.find_elements(By.TAG_NAME, "option")

        for option in list_options:
            if option.text == "Depósitos Judiciais da Justiça Estadual":
                sleep(0.5)
                option.click()
                break

        sleep(0.5)
        captchainput: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[id="autoCaptcha"',
            )),
        )
        val_captcha = captchainput.get_attribute("value")

        inputcaptcha: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'input[id="j_id5:filtroView:j_id6:j_id17:captchaView:cpatchaTextBox"]',
                ),
            ),
        )
        inputcaptcha.send_keys(val_captcha.replace(",", ""))

        next_btn = self.driver.find_element(
            By.CSS_SELECTOR, 'input[class="hand btnConfirmar"]'
        )
        next_btn.click()

        sleep(2)
        next_btn: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'a[id="j_id5:filtroView:mensagemView:j_id77:btnProsseguir',
                ),
            ),
        )
        next_btn.click()

    def locale_proc(self) -> None:
        """Define tribunal, comarca, vara, and agency based on user-provided data inputs.

        Allow the script to select appropriate locale and proceed with deposit steps.
        """
        self.interact.wait_caixa()

        message = "Informando tribunal"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        lista_tribunal: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'select[id="j_id5:filtroView:formFormulario:coTribunal"]',
                ),
            ),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_tribunal:
            item: WebElement = item
            if str(self.bot_data.get("TRIBUNAL")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()

        message = "Informando comarca"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        lista_comarca: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'select[id="j_id5:filtroView:formFormulario:coComarca"]',
            )),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_comarca:
            item: WebElement = item
            if str(self.bot_data.get("COMARCA")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()
        message = "Informando vara"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        lista_vara: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'select[id="j_id5:filtroView:formFormulario:coVara"]',
            )),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_vara:
            item: WebElement = item
            if str(self.bot_data.get("VARA")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()
        message = "Informando agencia"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        lista_agencia: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'select[id="j_id5:filtroView:formFormulario:coAgencia"]',
            )),
        ).find_elements(By.TAG_NAME, "option")
        for item in lista_agencia:
            item: WebElement = item
            if str(self.bot_data.get("AGENCIA")).lower() in item.text.lower():
                item.click()
                break

    def proc_nattribut(self) -> None:
        """Set the process number and action type for the judicial deposit context.

        Insert the required process details, ensuring the correct action type
        and default deposit nature.
        """
        numprocess = self.bot_data.get("NUMERO_PROCESSO").split(".")
        numproc_formated = (
            f"{numprocess[0]}.{numprocess[1]}.{numprocess[3]}.{numprocess[4]}"
        )

        self.interact.wait_caixa()
        message = "Informando numero do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        num_process: WebElement = self.wait.until(
            ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'input[id="j_id5:filtroView:formFormulario:nuProcessoCNJ"]',
                ),
            ),
        )
        num_process.send_keys(numproc_formated)

        self.interact.wait_caixa()
        message = "Informando tipo da ação do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        list_type_acao_process = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:idOrigemAcao"]',
        ).find_elements(By.TAG_NAME, "option")
        for item in list_type_acao_process:
            item: WebElement = item
            if str(self.bot_data.get("TIPO_ACAO")).lower() in item.text.lower():
                item.click()
                break

        self.interact.wait_caixa()
        message = "Informando natureza tributaria"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        natureza_tributaria = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:naturezaAcao"]',
        ).find_elements(By.TAG_NAME, "option")[2]
        natureza_tributaria.click()

    def dados_partes(self) -> None:
        """Fill in party information, including name and document details.

        Determine the document type (CPF or CNPJ) automatically and populate
        corresponding fields for both plaintiff (autor) and defendant (réu).
        """
        self.interact.wait_caixa()
        message = "Informando nome do autor"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        campo_nome_autor = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:nomeAutor"]',
        )
        campo_nome_autor.send_keys(self.bot_data.get("AUTOR"))

        self.interact.wait_caixa()
        message = "Informando tipo de documento do autor"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        doct_type = self.count_doc(self.bot_data.get("CPF_CNPJ_AUTOR"))

        if not doct_type:
            return

        doctype_autor = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:tipoDocAutor"]',
        ).find_elements(By.TAG_NAME, "option")

        for item in doctype_autor:
            item: WebElement = item
            if item.text.lower() == doct_type.lower():
                item.click()
                break

        self.interact.wait_caixa()
        message = "Informando documento do autor"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.interact.wait_caixa()
        campo_doc_autor = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:codDocAutor"]',
        )
        doc_autor = (
            str(self.bot_data.get("CPF_CNPJ_AUTOR"))
            .replace("-", "")
            .replace(".", "")
            .replace("/", "")
        )
        campo_doc_autor.send_keys(doc_autor)

        self.interact.wait_caixa()
        self.meesage = "Informando réu"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        campo_nome_reu = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:nomeReu"]',
        )

        contraria = None
        for passivo in ["réu", "reu"]:
            contraria = self.bot_data.get(passivo.upper(), None)
            if contraria is not None:
                break

        campo_nome_reu.send_keys(self.bot_data.get("REU", contraria))

        doct_type = self.count_doc(self.bot_data.get("CPF_CNPJ_REU"))

        self.interact.wait_caixa()
        doctype_reu = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:tipoDocReu"]',
        ).find_elements(By.TAG_NAME, "option")
        for item in doctype_reu:
            if item.text.lower() == doct_type.lower():
                item.click()
                break

        self.interact.wait_caixa()
        message = "Informando tipo de documento réu"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        campo_doc_reu = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:codDocReu"]',
        )
        doc_reu = (
            str(self.bot_data.get("CPF_CNPJ_REU"))
            .replace(".", "")
            .replace("-", "")
            .replace("/", "")
        )
        campo_doc_reu.send_keys(doc_reu)

    def info_deposito(self) -> None:
        """Insert depositor's indicator and deposit amount into the form.

        Identify the depositor (usually 'Réu') and format the deposit value
        to comply with input requirements.
        """
        self.interact.wait_caixa()
        message = "Informando indicador depositante"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        indicador_depositante = self.driver.find_element(
            By.CSS_SELECTOR,
            'select[id="j_id5:filtroView:formFormulario:idDepositante"]',
        ).find_elements(By.TAG_NAME, "option")

        for item in indicador_depositante:
            if item.text.lower() == "réu":
                item.click()
                break

        self.interact.wait_caixa()
        message = "Informando valor do depósito"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        campo_val_deposito = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[id="j_id5:filtroView:formFormulario:valorDeposito"]',
        )

        val_deposito = str(self.bot_data.get("VALOR_CALCULADO"))

        if "," not in val_deposito:
            val_deposito = f"{val_deposito},00"
        campo_val_deposito.send_keys(val_deposito)

    def make_doc(self) -> None:
        """Generate the deposit document and initiate the PDF download sequence.

        Trigger the system to create a deposit PDF that is saved for further
        renaming and data extraction.
        """
        self.interact.wait_caixa()
        message = "Gerando documento"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        make_id = self.driver.find_element(
            By.CSS_SELECTOR, 'input[id="j_id5:filtroView:formFormulario:j_id248"]'
        )
        make_id.click()

        self.interact.wait_caixa()
        message = "Baixando documento"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )
        download_pdf = self.driver.find_element(
            By.CSS_SELECTOR, 'a[id="j_id5:filtroView:formFormulario:j_id554"]'
        )
        download_pdf.click()

    def rename_pdf(self) -> str:
        """Rename and relocate the downloaded PDF with a standardized file name.

        Use bot_data for constructing the new name and move the file to its
        final output directory, then return the new filename.

        Returns:
            str: New PDF filename after relocation.

        """
        pgto_name = self.bot_data.get("NOME_CUSTOM", "Guia De Depósito")

        numproc = self.bot_data.get("NUMERO_PROCESSO")
        pdf_name = (
            f"{pgto_name} - {numproc} - {self.bot_data.get('AUTOR')} - {self.pid}.pdf"
        )
        sleep(10)

        caminho_old_pdf = os.path.join(self.output_dir_path, "guia_boleto.pdf")
        renamepdf = os.path.join(self.output_dir_path, pdf_name)

        sleep(5)
        shutil.move(caminho_old_pdf, renamepdf)

        return pdf_name

    def get_val_doc_and_codebar(self, pdf_name: str) -> None:
        """Extract deposit values and barcode from the specified PDF.

        Open the PDF, locate barcodes and monetary values, then package the
        results into a structured list for further processing.

        Args:
            pdf_name (str): PDF file name to parse.

        Returns:
            list: Contains process information, including barcodes and deposit data.

        """
        sleep(0.5)

        path_pdf = os.path.join(self.output_dir_path, pdf_name)
        # Inicialize uma lista para armazenar os números encontrados
        bar_code = ""
        numeros_encontrados = []

        # Expressão regular para encontrar números nesse formato
        pattern = r"\b\d{5}\.\d{5}\s*\d{5}\.\d{6}\s*\d{5}\.\d{6}\s*\d\s*\d{14}\b"

        pdf_file = path_pdf
        read = PdfReader(pdf_file)

        for page in read.pages:
            text = page.extract_text()

            with suppress(Exception):
                # Use a expressão regular para encontrar números
                numeros = re.findall(pattern, text)

                # Adicione os números encontrados à lista
                numeros_encontrados.extend(numeros)

        # Imprima os números encontrados
        for numero in numeros_encontrados:
            numero = str(numero)
            bar_code = numero.replace("  ", "").replace(" ", "").replace(".", " ")

        return [
            self.bot_data.get("NUMERO_PROCESSO"),
            self.bot_data.get("TEXTO_DESC", ""),
            self.bot_data.get("VALOR_CALCULADO"),
            self.bot_data.get("DATA_PGTO", ""),
            "condenação",
            "JEC",
            self.bot_data.get("VIA_CONDENACAO", ""),
            bar_code,
            pdf_name,
        ]
