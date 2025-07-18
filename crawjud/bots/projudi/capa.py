"""Module: capa.

Extract and manage process details from Projudi by scraping and formatting data.
"""

import re
import shutil
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Self

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError, FileError, ProcNotFoundError

# from memory_profiler import profile
# fp = open("memory_profiler_capa_projudi.log", "+w")


class Capa(CrawJUD):
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

    def execution(self) -> None:
        """Execute the main processing loop to extract process information.

        Iterates over each data row and queues process data extraction.
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
        """Handle the process information extraction queue by refreshing the driver.

        Raises:
            ExecutionError: If the process is not found or extraction fails.

        """
        try:
            self.prt.print_msg(
                f"Buscando processo nº {self.bot_data['NUMERO_PROCESSO']}"
            )
            search = self.search_bot.search(self.bot_data)
            if search is not True:
                raise ProcNotFoundError(self.pid, message="Processo não encontrado!")

            message = "Processo encontrado"
            typelog = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=typelog
            )
            trazer_copia = self.bot_data.get("TRAZER_COPIA", "não")

            self.driver.refresh()
            data = self.get_process_informations()

            if trazer_copia and trazer_copia.lower() == "sim":
                data = self.copia_pdf(data)

            self.append_success(
                [data], "Informações do processo extraidas com sucesso!"
            )

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def copia_pdf(
        self, data: dict[str, str | int | datetime]
    ) -> dict[str, str | int | datetime]:
        """Extract the movements of the legal proceedings and saves a PDF copy."""
        id_proc = self.driver.find_element(
            By.CSS_SELECTOR, 'input[name="id"]'
        ).get_attribute("value")

        btn_exportar = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'input[id="btnMenuExportar"]',
            ))
        )
        time.sleep(0.5)
        btn_exportar.click()

        btn_exportar_processo = self.wait.until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[id="exportarProcessoButton"]'),
            )
        )
        time.sleep(0.5)
        btn_exportar_processo.click()

        def unmark_gen_mov() -> None:
            time.sleep(0.5)
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="gerarMovimentacoes"][value="false"]',
                ))
            ).click()

        def unmark_add_validate_tag() -> None:
            time.sleep(0.5)
            self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'input[name="adicionarTarjaValidacao"][value="false"]',
                ))
            ).click()

        def export() -> None:
            message = "Baixando cópia integral do processo..."
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            time.sleep(5)

            n_processo = self.bot_data.get("NUMERO_PROCESSO")
            path_pdf = Path(self.output_dir_path).joinpath(
                f"Cópia Integral - {n_processo} - {self.pid}.pdf"
            )

            # # Get cookies from ChromeDriver session
            # cookies = {cookie["name"]: cookie["value"] for cookie in self.driver.get_cookies()}

            # form = self.driver.find_element(
            #     By.CSS_SELECTOR,
            #     'form[id="processoExportarForm"]',
            # )
            # form_path = form.get_attribute("action")
            # url = form_path
            # value_achives: list[str] = []
            # for file_ in form.find_elements(
            #     By.CSS_SELECTOR,
            #     'input[name="arquivos"]',
            # ):
            #     value_achives.append(file_.get_attribute("value"))

            # archives = ",".join(value_achives)

            # form_values = {
            #     "selectedItems": archives,
            # }

            # other_inputs = form.find_elements(
            #     By.XPATH,
            #     ".//input[not(contains(@name, 'arquivos'))][not(contains(@name, 'selectedItems'))]",
            # )
            # for input_ in other_inputs:
            #     if input_.get_attribute("name") and input_.get_attribute("value"):
            #         if input_.get_attribute("name") == "adicionarCapa":
            #             form_values.update({input_.get_attribute("name"): "true"})
            #             continue

            #         form_values.update(
            #             {input_.get_attribute("name"): input_.get_attribute("value")},
            #         )

            # # Download using requests
            # try:
            #     response = requests.post(url=self.driver.current_url, data=form_values, cookies=cookies, timeout=60)

            # except Exception as e:
            #   raise e

            # if response.status_code == 200:
            #     with open(path_pdf, "wb") as f:
            #         f.write(response.content)

            #     is_pdf = mimetypes.guess_type(path_pdf)[0]
            #     if is_pdf != "application/pdf":

            # elif response.status_code != 200:
            # Fallback to ChromeDriver download if requests fails

            btn_exportar = self.driver.find_element(
                By.CSS_SELECTOR, 'input[name="btnExportar"]'
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
                raise FileError(
                    message="Arquivo não encontrado!", bot_execution_id=self.pid
                )

            shutil.move(path_copia, path_pdf)

            time.sleep(0.5)
            data.update({"CÓPIA_INTEGRAL": path_pdf.name})

        unmark_gen_mov()
        unmark_add_validate_tag()
        export()

        return data

    def get_process_informations(self) -> dict[str, str | int | datetime]:
        """Extract detailed process information from the current web page.

        Returns:
            list: A list of dictionaries containing formatted process information.

        Raises:
            Exception: If extraction encounters an error.

        """
        try:
            grau = self.bot_data.get("GRAU", 1)

            if grau is None:
                grau = 1

            if isinstance(grau, str):
                grau = grau.strip()

            grau = int(grau)
            process_info: dict[str, str | int | datetime] = {}
            process_info.update({
                "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO")
            })

            def format_vl_causa(valor_causa: str) -> float | str:
                """Format the value of the cause by removing currency symbols and converting to float.

                Args:
                    valor_causa (str): The raw value string.

                Returns:
                    float | str: The formatted value as float or original string if no match.

                """
                if "¤" in valor_causa:
                    valor_causa = valor_causa.replace("¤", "")

                pattern = r"(?<!\S)(?:US\$[\s]?|R\$[\s]?|[\$]?)\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?(?!\S)"
                matches = re.findall(pattern, valor_causa)
                if len(matches) > 0:

                    def convert_to_float(value: str) -> float:
                        """Convert a formatted string to float.

                        Args:
                            value (str): The string to convert.

                        Returns:
                            float: The converted float value.

                        """
                        # Remover símbolos de moeda e espaços
                        value = re.sub(r"[^\d.,]", "", value)

                        # Identificar se o formato é BRL (com vírgula para decimais) ou USD (com ponto para decimais)
                        if "," in value and "." in value:
                            # Assumir formato USD se houver tanto ',' quanto '.'
                            parts = value.split(".")
                            if len(parts[-1]) == 2:
                                value = value.replace(",", "")
                            elif not len(parts[-1]) == 2:
                                value = value.replace(".", "").replace(",", ".")
                        elif "," in value:
                            # Assumir formato BRL
                            value = value.replace(".", "").replace(",", ".")
                        elif "." in value:
                            # Assumir formato USD
                            value = value.replace(",", "")

                        return float(value)

                    return convert_to_float(matches[0])

                return valor_causa

            message = f"Obtendo informações do processo {self.bot_data.get('NUMERO_PROCESSO')}..."
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

            btn_infogeral = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.btn_infogeral
            )
            btn_infogeral.click()

            includecontent: list[WebElement] = []

            element_content = self.elements.primeira_instform1
            element_content2 = self.elements.primeira_instform2

            if grau == 2:
                element_content = self.elements.segunda_instform
                element_content2 = element_content

            includecontent.append(
                self.driver.find_element(By.CSS_SELECTOR, element_content)
            )
            includecontent.append(
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        element_content2,
                    ))
                )
            )

            for incl in includecontent:
                with suppress(StaleElementReferenceException):
                    itens = list(
                        filter(
                            lambda x: len(x.find_elements(By.TAG_NAME, "td")) > 1,
                            incl.find_element(By.TAG_NAME, "tbody").find_elements(
                                By.TAG_NAME, "tr"
                            ),
                        ),
                    )

                    for item in itens:
                        labels = list(
                            filter(
                                lambda x: x.text.strip() != "",
                                item.find_elements(
                                    By.CSS_SELECTOR, "td.label, td.labelRadio > label"
                                ),
                            ),
                        )
                        # para teste
                        # for value in item.find_elements(By.CSS_SELECTOR, "td"):
                        #     print(value.text.strip())

                        values = list(
                            filter(
                                lambda x: x.text.strip() != ""
                                and not x.get_attribute("class"),
                                item.find_elements(By.TAG_NAME, "td"),
                            ),
                        )

                        for _, label in enumerate(labels):
                            if len(labels) != len(values):
                                continue

                            not_formated_label = label.text
                            label_text = (
                                self.format_string(label.text)
                                .upper()
                                .replace(" ", "_")
                            )

                            indice = labels.index(label)
                            value_text = values[indice].text

                            if label_text == "VALOR_DA_CAUSA":
                                value_text = format_vl_causa(value_text)

                            elif (
                                "DATA" in label_text
                                or "DISTRIBUICAO" in label_text
                                or "AUTUACAO" in label_text
                            ):
                                if " às " in value_text:
                                    value_text = value_text.split(" às ")[0]

                                if self.text_is_a_date(value_text) is True:
                                    value_text = datetime.strptime(
                                        value_text, "%d/%m/%Y"
                                    )

                            elif not_formated_label != value_text:
                                value_text = " ".join(value_text.split(" ")).upper()

                            else:
                                continue

                            process_info.update({label_text: value_text})

            btn_partes = self.elements.btn_partes
            if grau == 2:
                btn_partes = btn_partes.replace("2", "1")

            btn_partes = self.driver.find_element(By.CSS_SELECTOR, btn_partes)
            btn_partes.click()

            try:
                includecontent = self.driver.find_element(
                    By.ID, self.elements.includecontent_capa
                )
            except Exception:
                time.sleep(3)
                self.driver.refresh()
                time.sleep(1)
                includecontent = self.driver.find_element(
                    By.ID, self.elements.includecontent_capa
                )

            result_table = includecontent.find_elements(
                By.CLASS_NAME, self.elements.resulttable
            )

            for pos, parte_info in enumerate(result_table):
                h4_name = list(
                    filter(
                        lambda x: x.text != "" and x is not None,
                        includecontent.find_elements(By.TAG_NAME, "h4"),
                    ),
                )
                tipo_parte = (
                    self.format_string(h4_name[pos].text).replace(" ", "_").upper()
                )

                nome_colunas = []

                for column in parte_info.find_element(
                    By.TAG_NAME, "thead"
                ).find_elements(By.TAG_NAME, "th"):
                    nome_colunas.append(column.text.upper())

                for parte in parte_info.find_element(
                    By.TAG_NAME, "tbody"
                ).find_elements(
                    By.XPATH,
                    self.elements.table_moves,
                ):
                    for pos_, nome_coluna in enumerate(nome_colunas):
                        key = "_".join((
                            self.format_string(nome_coluna).replace(" ", "_").upper(),
                            tipo_parte,
                        ))
                        value = parte.find_elements(By.TAG_NAME, "td")[pos_].text

                        if value:
                            " ".join(value.split(" "))

                            if "\n" in value:
                                value = " | ".join(value.split("\n"))
                                process_info.update({key: value})
                                continue

                            process_info.update({key: value})

            return process_info

        except Exception as e:
            raise e
