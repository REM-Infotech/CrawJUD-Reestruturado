"""Module for managing deadline tracking and recording in the ELAW system.

This module provides functionality for creating, updating and tracking deadlines within
the ELAW system. It automates the process of recording and monitoring time-sensitive tasks.

Classes:
    Prazos: Manages deadline entries by extending the CrawJUD base class
"""

from __future__ import annotations

import os
from contextlib import suppress
from typing import Self

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError


class Prazos(CrawJUD):
    """The Prazos class extends CrawJUD to handle deadline-related tasks within the application.

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
        """Execute the main processing loop for deadlines."""
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
        """Handle the deadline queue processing.

        Raises:
            ExecutionError: If an error occurs during execution.

        """
        try:
            search = self.search_bot()
            if not search:
                self.message = "Buscando Processo"
                raise ExecutionError(message="Não Encontrado!")

            comprovante = ""
            self.data_Concat = f"{self.bot_data['DATA_AUDIENCIA']} {self.bot_data['HORA_AUDIENCIA']}"
            self.message = "Processo Encontrado!"
            self.type_log = "log"
            self.prt()

            self.TablePautas()
            chk_lancamento = self.CheckLancamento()

            if chk_lancamento:
                self.message = "Já existe lançamento para esta pauta"
                self.type_log = "info"
                chk_lancamento.update({"MENSAGEM_COMCLUSAO": "REGISTROS ANTERIORES EXISTENTES!"})

                comprovante = chk_lancamento

            if not comprovante:
                self.NovaPauta()
                self.save_Prazo()
                comprovante = self.CheckLancamento()
                if not comprovante:
                    raise ExecutionError(message="Não foi possível comprovar lançamento, verificar manualmente")

                self.message = "Pauta lançada!"

            self.append_success([comprovante], self.message)

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def TablePautas(self) -> None:  # noqa: N802
        """Verify if there are existing schedules for the specified day.

        Raises:
            ExecutionError: If an error occurs during the verification process.

        """
        try:
            switch_pautaandamento = self.driver.find_element(By.CSS_SELECTOR, self.elements.switch_pautaandamento)

            switch_pautaandamento.click()

            self.message = f"Verificando se existem pautas para o dia {self.data_Concat}"
            self.type_log = "log"
            self.prt()

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def NovaPauta(self) -> None:  # noqa: N802
        """Launch a new audience schedule.

        Raises:
            ExecutionError: If unable to launch a new audience.

        """
        try:
            self.message = "Lançando nova audiência"
            self.type_log = "log"
            self.prt()

            btn_novaaudiencia = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.btn_novaaudiencia)),
            )

            btn_novaaudiencia.click()

            # Info tipo Audiencia
            self.message = "Informando tipo de audiência"
            self.type_log = "log"
            self.prt()

            selectortipoaudiencia: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.selectortipoaudiencia)),
            )

            items = selectortipoaudiencia.find_elements(By.TAG_NAME, "option")
            opt_itens: dict[str, str] = {}
            for item in items:
                value_item = item.get_attribute("value")
                text_item = self.driver.execute_script(f"return $(\"option[value='{value_item}']\").text();")

                opt_itens.update({text_item.upper(): value_item})

            value_opt = opt_itens.get(self.bot_data["TIPO_AUDIENCIA"].upper())
            if value_opt:
                command = f"$('{self.elements.selectortipoaudiencia}').val(['{value_opt}']);"
                self.driver.execute_script(command)

                command2 = f"$('{self.elements.selectortipoaudiencia}').trigger('change');"
                self.driver.execute_script(command2)

            # Info Data Audiencia
            self.message = "Informando data da Audiência"
            self.type_log = "log"
            self.prt()

            DataAudiencia: WebElement = self.wait.until(  # noqa: N806
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.DataAudiencia)),
            )

            DataAudiencia.send_keys(self.data_Concat)

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def save_Prazo(self) -> None:  # noqa: N802
        """Save the newly created deadline.

        Raises:
            ExecutionError: If unable to save the deadline.

        """
        try:
            self.message = "Salvando..."
            self.type_log = "log"
            self.prt()

            btn_salvar = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_salvar)

            btn_salvar.click()

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e

    def CheckLancamento(self) -> dict[str, str] | None:  # noqa: N802
        """Check if the deadline has been successfully recorded.

        Returns:
            dict[str, str] | None: Details of the recorded deadline or None if not found.

        Raises:
            ExecutionError: If unable to verify the deadline record.

        """
        try:
            tableprazos: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.tableprazos)),
            )

            tableprazos: list[WebElement] = tableprazos.find_elements(By.TAG_NAME, "tr")

            data = None
            for item in tableprazos:
                if item.text == "Nenhum registro encontrado!":
                    return None

                data_Prazo = str(item.find_elements(By.TAG_NAME, "td")[4].text)  # noqa: N806

                tipo = str(item.find_elements(By.TAG_NAME, "td")[5].text)

                chk_tipo = tipo.upper() == "AUDIÊNCIA"
                chk_dataAudiencia = data_Prazo == self.data_Concat  # noqa: N806

                if chk_tipo and chk_dataAudiencia:
                    nProc_pid = f"{self.bot_data['NUMERO_PROCESSO']} - {self.pid}"  # noqa: N806

                    nameComprovante = f"Comprovante - {nProc_pid}.png"  # noqa: N806
                    idPrazo = str(item.find_elements(By.TAG_NAME, "td")[2].text)  # noqa: N806

                    item.screenshot(os.path.join(self.output_dir_path, nameComprovante))

                    data = {
                        "NUMERO_PROCESSO": str(self.bot_data["NUMERO_PROCESSO"]),
                        "MENSAGEM_COMCLUSAO": "PRAZO LANÇADO",
                        "ID_PRAZO": idPrazo,
                        "NOME_COMPROVANTE": nameComprovante,
                    }

            return data

        except Exception as e:
            raise ExecutionError(exception=e, bot_execution_id=self.pid) from e
