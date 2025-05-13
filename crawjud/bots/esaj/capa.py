"""Manage capa operations and extract process information for CrawJUD-Bots.

This module executes the workflow to search and process process details,
ensuring detailed extraction and logging of information.
"""

from contextlib import suppress
from typing import Self

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError


class Capa(CrawJUD):
    """Perform capa tasks by searching and extracting process details robustly.

    This class handles process information retrieval including form extraction
    and logging. It supports multiple process degrees.
    """

    @classmethod
    def initialize(cls, *args: str | int, **kwargs: str | int) -> Self:
        """Initialize a Capa instance with given parameters and settings.

        Args:
            *args (str|int): Positional arguments.
            **kwargs (str|int): Keyword arguments.

        Returns:
            Self: A new instance of Capa.

        """
        return cls(*args, **kwargs)

    def execution(self) -> None:
        """Execute capa processing by iterating over rows with robust error handling.

        Iterates over the dataframe, renews sessions when expired, and logs errors
        for each process.
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
        """Queue capa tasks by searching for process data and appending details to logs.

        Calls the search method and retrieves detailed process information.
        """
        try:
            search = self.search_bot()

            if search is False:
                raise ExecutionError(message="Processo não encontrado.")

            self.append_success(self.get_process_informations())

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def get_process_informations(self) -> list:
        """Extract and return detailed process information from the web elements.

        Returns:
            list: A structured list containing process details such as area, forum, and value.

        Note:
            Extraction varies by process degree.

        """
        # chk_advs = ["Advogada", "Advogado"]
        # adv_polo_ativo = "Não consta"
        # adv_polo_passivo = "Não consta"

        self.message = f"Extraindo informações do processo nº{self.bot_data.get('NUMERO_PROCESSO')}"
        self.type_log = "log"
        self.prt()

        grau = self.bot_data.get("GRAU", 1)

        if not grau:
            grau = 1

        elif isinstance(grau, str):
            if "º" in grau:
                grau = grau.replace("º", "")

            grau = int(grau)

        self.driver.execute_script("$('div#maisDetalhes').show()")

        data = {"NUMERO_PROCESSO": ""}

        sumary_1_esaj = self.wait.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, self.elements.sumary_header_1)),
        )

        sumary_2_esaj = self.wait.until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, self.elements.sumary_header_2)),
        )

        list_sumary = [sumary_1_esaj, sumary_2_esaj]

        for pos_, sumary in enumerate(list_sumary):
            for pos, rows in enumerate(sumary):
                subitems_sumary = rows.find_elements(By.CSS_SELECTOR, self.elements.rows_sumary_)

                for item in subitems_sumary:
                    if pos == 0 and pos_ == 0:
                        num_proc = item.find_element(By.CLASS_NAME, self.elements.numproc).text
                        status_proc = "Em Andamento"
                        with suppress(NoSuchElementException):
                            status_proc = item.find_element(By.CLASS_NAME, self.elements.statusproc).text

                        data.update({"NUMERO_PROCESSO": num_proc, "STATUS": status_proc.upper()})
                        continue

                    value = None
                    title = item.find_element(By.CLASS_NAME, self.elements.nameitemsumary).text

                    if title:
                        title = title.upper()

                    if " " in title:
                        title = "_".join([ttl for ttl in title.split(" ") if ttl])

                    with suppress(NoSuchElementException):
                        value = item.find_element(By.CSS_SELECTOR, self.elements.valueitemsumary).text

                    if not value:
                        with suppress(NoSuchElementException):
                            element_search = self.elements.value2_itemsumary.get(title)

                            if element_search:
                                value = item.find_element(By.CSS_SELECTOR, element_search).text

                                if title == "OUTROS_ASSUNTOS":
                                    value = " ".join([val for val in value.split(" ") if val])

                    if value:
                        data.update({title: value.upper()})

        table_partes = self.driver.find_element(By.ID, self.elements.area_selecao)
        for group_parte in table_partes.find_elements(By.TAG_NAME, "tr"):
            pos_repr = 0
            type_parte = self.format_string(group_parte.find_elements(By.TAG_NAME, "td")[0].text.upper())

            info_parte = group_parte.find_elements(By.TAG_NAME, "td")[1]
            info_parte_text = info_parte.text.split("\n")
            if "\n" in info_parte.text:
                for attr_parte in info_parte_text:
                    if ":" in attr_parte:
                        representante = attr_parte.replace("  ", "").split(":")
                        tipo_representante = representante[0].upper()
                        nome_representante = representante[1].upper()
                        key = {f"{tipo_representante}_{type_parte}": nome_representante}

                        doc_ = "Não consta"
                        with suppress(NoSuchElementException, IndexError):
                            doc_ = info_parte.find_elements(By.TAG_NAME, "input")[pos_repr]
                            doc_ = doc_.get_attribute("value")

                        key_doc = {f"DOC_{tipo_representante}_{type_parte}": doc_}

                        pos_repr += 1

                        data.update(key)
                        data.update(key_doc)

                    elif ":" not in attr_parte:
                        key = {type_parte: attr_parte}
                        data.update(key)

            elif "\n" not in info_parte_text:
                key = {type_parte: info_parte.text}
                data.update(key)

        return [data]
