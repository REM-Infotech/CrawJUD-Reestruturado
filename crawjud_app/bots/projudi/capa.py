"""Module: capa.

Extract and manage process details from Projudi by scraping and formatting data.
"""

import re
import shutil
import time
import traceback
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Self

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from controllers.bots.master.bot_head import HeadBot
from crawjud_app.common.exceptions.bot import ExecutionError


class Capa(HeadBot):
    """Extract process information from Projudi and populate structured data.

    This class extends CrawJUD to click through information panels,
    extract process data and participant details, and format them accordingly.
    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize a Capa instance with provided arguments.

        Args:
            *args (tuple[str | int]): Variable length positional arguments.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        Returns:
            Self: The initialized Capa instance.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Capa instance and start authentication.

        Args:
            *args (tuple[str | int]): Positional arguments.
            **kwargs (dict[str, str | int]): Keyword arguments.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the main processing loop to extract process information.

        Iterates over each data row and queues process data extraction.
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
                self.logger.exception(str(e))
                old_message = None

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
        """Handle the process information extraction queue by refreshing the driver.

        Raises:
            ExecutionError: If the process is not found or extraction fails.

        """
        try:
            search = self.search_bot()
            trazer_copia = self.bot_data.get("TRAZER_COPIA", "não")
            if search is not True:
                raise ExecutionError(message="Processo não encontrado!")

            self.driver.refresh()
            data = self.get_process_informations()

            if trazer_copia and trazer_copia.lower() == "sim":
                data = self.copia_pdf(data)

            self.append_success(
                [data],
                "Informações do processo extraidas com sucesso!",
            )

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            self.logger.exception(str(e))
            raise ExecutionError(e=e) from e

    def copia_pdf(
        self,
        data: dict[str, str | int | datetime],
    ) -> dict[str, str | int | datetime]:
        """Extract the movements of the legal proceedings and saves a PDF copy."""
        id_proc = self.driver.find_element(
            By.CSS_SELECTOR,
            'input[name="id"]',
        ).get_attribute("value")

        btn_exportar = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[id="btnMenuExportar"]',
            )),
        )
        time.sleep(0.5)
        btn_exportar.click()

        btn_exportar_processo = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[id="exportarProcessoButton"]'),
            ),
        )
        time.sleep(0.5)
        btn_exportar_processo.click()

        def unmark_gen_mov() -> None:
            time.sleep(0.5)
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="gerarMovimentacoes"][value="false"]',
                )),
            ).click()

        def unmark_add_validate_tag() -> None:
            time.sleep(0.5)
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="adicionarTarjaValidacao"][value="false"]',
                )),
            ).click()

        def export() -> None:
            self.message = "Baixando cópia integral do processo..."
            self.type_log = "log"
            self.prt()
            time.sleep(5)

            n_processo = self.bot_data.get("NUMERO_PROCESSO")
            path_pdf = Path(self.output_dir_path).joinpath(
                f"Cópia Integral - {n_processo} - {self.pid}.pdf",
            )

            btn_exportar = self.driver.find_element(
                By.CSS_SELECTOR,
                'input[name="btnExportar"]',
            )
            btn_exportar.click()

            count = 0
            time.sleep(5)
            path_copia = self.output_dir_path.joinpath(f"{id_proc}.pdf").resolve()

            while count <= 300:
                if path_copia.exists():
                    break

                time.sleep(2)
                count += 1

            if not path_copia.exists():
                raise ExecutionError(message="Arquivo não encontrado!")

            shutil.move(path_copia, path_pdf)

            time.sleep(0.5)
            data.update({"CÓPIA_INTEGRAL": path_pdf.name})

        unmark_gen_mov()
        unmark_add_validate_tag()
        export()

        return data

    def get_process_informations(self) -> dict[str, str | int | datetime]:
        """Extrai informações detalhadas do processo da página atual do Projudi.

        Returns:
            dict[str, str | int | datetime]: Dicionário com informações formatadas do processo.

        Raises:
            Exception: Se ocorrer erro na extração.

        """
        try:
            grau = self._get_grau()
            process_info: dict[str, str | int | datetime] = {
                "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
            }

            self._log_obtendo_informacoes()

            self._extrai_info_geral(process_info, grau)
            self._extrai_partes(process_info, grau)

            return process_info

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise e

    def _get_grau(self) -> int:
        """Obtém e formata o grau do processo.

        Returns:
            int: Grau do processo.

        """
        grau = self.bot_data.get("GRAU", 1)
        if grau is None:
            grau = 1
        if isinstance(grau, str):
            grau = grau.strip()
        return int(grau)

    def _log_obtendo_informacoes(self) -> None:
        """Exibe log de obtenção de informações do processo."""
        self.message = f"Obtendo informações do processo {self.bot_data.get('NUMERO_PROCESSO')}..."
        self.type_log = "log"
        self.prt()

    def _extrai_info_geral(
        self,
        process_info: dict[str, str | int | datetime],
        grau: int,
    ) -> None:
        """Extrai informações gerais do processo.

        Args:
            process_info (dict): Dicionário de informações do processo.
            grau (int): Grau do processo.

        """
        btn_infogeral = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.btn_infogeral,
        )
        btn_infogeral.click()

        element_content = self.elements.primeira_instform1
        element_content2 = self.elements.primeira_instform2
        if grau == 2:
            element_content = self.elements.segunda_instform
            element_content2 = element_content

        includecontent = [
            self.driver.find_element(By.CSS_SELECTOR, element_content),
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    element_content2,
                )),
            ),
        ]

        for incl in includecontent:
            self._extrai_tabela_info_geral(incl, process_info)

    def _extrai_tabela_info_geral(
        self,
        incl: WebElement,
        process_info: dict[str, str | int | datetime],
    ) -> None:
        """Extrai dados das tabelas de informações gerais.

        Args:
            incl (WebElement): Elemento da tabela.
            process_info (dict): Dicionário de informações do processo.

        """
        with suppress(StaleElementReferenceException):
            itens = [
                x
                for x in incl.find_element(By.TAG_NAME, "tbody").find_elements(
                    By.TAG_NAME,
                    "tr",
                )
                if len(x.find_elements(By.TAG_NAME, "td")) > 1
            ]
            for item in itens:
                labels = [
                    x
                    for x in item.find_elements(
                        By.CSS_SELECTOR,
                        "td.label, td.labelRadio > label",
                    )
                    if x.text.strip() != ""
                ]
                values = [
                    x
                    for x in item.find_elements(By.TAG_NAME, "td")
                    if x.text.strip() != "" and not x.get_attribute("class")
                ]
                if len(labels) != len(values):
                    continue
                for idx, label in enumerate(labels):
                    not_formated_label = label.text
                    label_text = (
                        self.format_string(label.text).upper().replace(" ", "_")
                    )
                    value_text = values[idx].text
                    value_text = self._format_value(
                        label_text,
                        not_formated_label,
                        value_text,
                    )
                    if value_text is not None:
                        process_info.update({label_text: value_text})

    def _format_value(
        self,
        label_text: str,
        not_formated_label: str,
        value_text: str,
    ) -> str | float | datetime | None:
        """Formata o valor extraído conforme o tipo de campo.

        Args:
            label_text (str): Texto do label formatado.
            not_formated_label (str): Texto original do label.
            value_text (str): Valor extraído.

        Returns:
            str | float | datetime | None: Valor formatado ou None.

        """
        if label_text == "VALOR_DA_CAUSA":
            return self._format_vl_causa(value_text)
        if (
            "DATA" in label_text
            or "DISTRIBUICAO" in label_text
            or "AUTUACAO" in label_text
        ):
            if " às " in value_text:
                value_text = value_text.split(" às ")[0]
            if self.text_is_a_date(value_text):
                return datetime.strptime(value_text, "%d/%m/%Y")
        elif not_formated_label != value_text:
            return " ".join(value_text.split(" ")).upper()
        return None

    def _format_vl_causa(self, valor_causa: str) -> float | str:
        """Formata o valor da causa removendo símbolos e convertendo para float.

        Args:
            valor_causa (str): Valor bruto.

        Returns:
            float | str: Valor formatado ou original.

        """
        if "¤" in valor_causa:
            valor_causa = valor_causa.replace("¤", "")
        pattern = r"(US\$|R\$|\$)?\s?\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?"
        matches = re.findall(pattern, valor_causa)
        if matches:
            return self._convert_to_float(matches[0])
        return valor_causa

    def _convert_to_float(self, value: str) -> float:
        """Convert string formatada para float.

        Args:
            value (str): Valor em string.

        Returns:
            float: Valor convertido.

        """
        value = re.sub(r"[^\d.,]", "", value)
        if "," in value and "." in value:
            parts = value.split(".")
            if len(parts[-1]) == 2:
                value = value.replace(",", "")
            else:
                value = value.replace(".", "").replace(",", ".")
        elif "," in value:
            value = value.replace(".", "").replace(",", ".")
        elif "." in value:
            value = value.replace(",", "")
        return float(value)

    def _extrai_partes(
        self,
        process_info: dict[str, str | int | datetime],
        grau: int,
    ) -> None:
        """Extrai informações das partes do processo.

        Args:
            process_info (dict): Dicionário de informações do processo.
            grau (int): Grau do processo.

        """
        btn_partes = self.elements.btn_partes
        if grau == 2:
            btn_partes = btn_partes.replace("2", "1")
        btn_partes = self.driver.find_element(By.CSS_SELECTOR, btn_partes)
        btn_partes.click()

        includecontent = self._get_includecontent_capa()
        result_table = includecontent.find_elements(
            By.CLASS_NAME,
            self.elements.resulttable,
        )
        h4_names = [
            x
            for x in includecontent.find_elements(By.TAG_NAME, "h4")
            if x.text != "" and x is not None
        ]
        for pos, parte_info in enumerate(result_table):
            tipo_parte = (
                self.format_string(h4_names[pos].text).replace(" ", "_").upper()
            )
            nome_colunas = [
                column.text.upper()
                for column in parte_info.find_element(
                    By.TAG_NAME,
                    "thead",
                ).find_elements(By.TAG_NAME, "th")
            ]
            self._extrai_tabela_partes(
                parte_info,
                nome_colunas,
                tipo_parte,
                process_info,
            )

    def _get_includecontent_capa(self) -> WebElement:
        """Obtém o elemento de conteúdo da capa.

        Returns:
            WebElement: Elemento de conteúdo.

        """
        try:
            return self.driver.find_element(By.ID, self.elements.includecontent_capa)
        except Exception:
            time.sleep(3)
            self.driver.refresh()
            time.sleep(1)
            return self.driver.find_element(By.ID, self.elements.includecontent_capa)

    def _extrai_tabela_partes(
        self,
        parte_info: WebElement,
        nome_colunas: list[str],
        tipo_parte: str,
        process_info: dict[str, str | int | datetime],
    ) -> None:
        """Extrai dados das tabelas de partes.

        Args:
            parte_info (WebElement): Elemento da tabela de partes.
            nome_colunas (list[str]): Lista de nomes das colunas.
            tipo_parte (str): Tipo da parte.
            process_info (dict): Dicionário de informações do processo.

        """
        linhas = parte_info.find_element(By.TAG_NAME, "tbody").find_elements(
            By.XPATH,
            self.elements.table_moves,
        )
        for parte in linhas:
            tds = parte.find_elements(By.TAG_NAME, "td")
            for pos_, nome_coluna in enumerate(nome_colunas):
                key = "_".join((
                    self.format_string(nome_coluna).replace(" ", "_").upper(),
                    tipo_parte,
                ))
                value = tds[pos_].text if pos_ < len(tds) else ""
                if value:
                    value = " ".join(value.split(" "))
                    if "\n" in value:
                        value = " | ".join(value.split("\n"))
                    process_info.update({key: value})
