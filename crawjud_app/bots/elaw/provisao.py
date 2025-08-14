"""Module for managing provision entries and updates in the ELAW system.

This module handles provision creation, updates and management within the ELAW system.
It automates the process of recording provisions and their associated documentation.

Classes:
    Provisao: Manages provision entries by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

import time
import traceback
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from controllers.bots.master.bot_head import ClassBot
from crawjud_app.common.exceptions.bot import ExecutionError

type_doc = {11: "cpf", 14: "cnpj"}


class Provisao(ClassBot):
    """The Provisao class extends CrawJUD to manage provisions within the application.

    Attributes:
        attribute_name (type): Description of the attribute.


    """

    @classmethod
    def initialize(
        cls,
        *args: str | int,
        **kwargs: str | int,
    ) -> Self:
        """Initialize bot instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        return cls(*args, **kwargs)

    def __init__(
        self,
        *args: str | int,
        **kwargs: str | int,
    ) -> None:
        """Initialize the Provisao instance.

        Args:
            *args (tuple[str | int]): Variable length argument list.
            **kwargs (dict[str, str | int]): Arbitrary keyword arguments.

        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the main processing loop for provisions."""
        frame = self.dataFrame()
        self.max_rows = len(frame)
        self.driver.maximize_window()
        self.driver.execute_script("document.body.style.zoom = '0.5'")
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
                # TODO(Nicholas Silva): Criação de Exceptions
                # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
                old_message = None
                windows = self.driver.window_handles

                if len(windows) == 0:
                    with suppress(Exception):
                        self.driver_launch(
                            message="Webdriver encerrado inesperadamente, reinicializando...",
                        )

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
        """Handle the provision queue processing.

        Raises:
            ExecutionError: If an error occurs during execution.

        """
        # module = "search_processo"

        try:
            search = self.search_bot()
            if search is True:
                self.type_log = "log"
                self.message = "Processo encontrado! Informando valores..."
                self.prt()

                calls = self.setup_calls()

                for call in calls:
                    call()

                self.save_changes()

            if search is False:
                raise ExecutionError(message="Processo não encontrado!")

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise e

    def chk_risk(self) -> None:
        """Check and select the appropriate risk type based on the provision label.

        Raises:
            None

        """
        label_risk = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.type_risk_label,
            )),
        )

        if label_risk.text == "Risco Quebrado":
            self.select2_elaw(self.elements.type_risk_select, "Risco")

    def setup_calls(self) -> list:
        """Configure sequence of method calls based on the provision data.

        Returns:
            list: A list of method references to be called.

        """
        calls = []

        # module = "get_valores_proc"
        get_valores = self.get_valores_proc()

        provisao = (
            str(self.bot_data.get("PROVISAO"))
            .replace("possivel", "possível")
            .replace("provavel", "provável")
            .lower()
        )

        chk_getvals1 = get_valores == "Contém valores"
        possible = provisao == "possível"

        if chk_getvals1 and possible:
            self.message = "Aviso: Já existe uma provisão possível cadastrada."
            self.type_log = "info"
            self.prt()

        edit_button: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_btn_edit,
            )),
        )
        edit_button.click()

        if get_valores == "Nenhum registro encontrado!":
            calls.append(self.add_new_valor)
            calls.append(self.edit_valor)
            calls.append(self.chk_risk)
            calls.append(self.set_valores)
            calls.append(self.informar_datas)

        elif get_valores == "Contém valores" or get_valores == "-":
            calls.append(self.edit_valor)
            calls.append(self.chk_risk)
            calls.append(self.set_valores)

            if provisao == "provável" or provisao == "possível":
                calls.append(self.informar_datas)

        calls.append(self.set_risk)
        calls.append(self.informar_motivo)

        return calls

    def get_valores_proc(self) -> str:
        """Retrieve the values related to the process.

        Returns:
            str: Description of the process values.

        """
        get_valores: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.ver_valores,
            )),
        )
        get_valores.click()

        check_exists_provisao: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.table_valores_css,
            )),
        )
        check_exists_provisao = check_exists_provisao.find_elements(By.TAG_NAME, "tr")

        for item in check_exists_provisao:
            item: WebElement = item
            item_text = str(item.text).split("\n")  # noqa: F841
            valueprovisao = item.find_elements(By.TAG_NAME, "td")[0].text
            with suppress(NoSuchElementException):
                valueprovisao = item.find_element(
                    By.CSS_SELECTOR,
                    self.elements.value_provcss,
                ).text

            if "-" in valueprovisao or valueprovisao == "Nenhum registro encontrado!":
                return valueprovisao

        return "Contém valores"

    def add_new_valor(self) -> None:
        """Add a new value entry.

        Raises:
            ExecutionError: If unable to update the provision.

        """
        try:
            div_tipo_obj: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.div_tipo_obj_css,
                )),
            )

            div_tipo_obj.click()

            item_obj_div: WebElement = (
                self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.itens_obj_div_css,
                    )),
                )
                .find_element(By.TAG_NAME, "ul")
                .find_elements(By.TAG_NAME, "li")[0]
                .find_element(By.CSS_SELECTOR, self.elements.checkbox)
            )

            item_obj_div.click()

            add_objeto = self.driver.find_element(
                By.CSS_SELECTOR,
                self.elements.botao_adicionar,
            )
            add_objeto.click()

            self.interact.sleep_load('div[id="j_id_8c"]')

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(
                message="Não foi possivel atualizar provisão",
                e=e,
            ) from e

    def edit_valor(self) -> None:
        """Edit an existing value entry."""
        editar_pedido: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.botao_editar,
            )),
        )
        editar_pedido.click()

    def set_valores(self) -> None:
        """Set the provision values.

        Raises:
            None

        """
        try:
            self.interact.sleep_load('div[id="j_id_2z"]')
            self.message = "Informando valores"
            self.type_log = "log"
            self.prt()

            row_valores = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "tbody[id='j_id_2z:j_id_32_2e:processoAmountObjetoDt_data']",
                )),
            ).find_elements(
                By.XPATH,
                './/tr[contains(@class, "ui-datatable-odd") or contains(@class, "ui-datatable-even")]',
            )

            for row_valor in row_valores:
                campo_valor_dml = row_valor.find_elements(By.TAG_NAME, "td")[
                    9
                ].find_element(By.CSS_SELECTOR, 'input[id*="_input"]')

                valor_informar = self.bot_data.get("VALOR_ATUALIZACAO")
                # if valor_informar == 0:
                #     raise ExecutionError(message="Valor de atualização inválido")

                campo_valor_dml.send_keys(Keys.CONTROL + "a")
                campo_valor_dml.send_keys(Keys.BACKSPACE)
                self.interact.sleep_load('div[id="j_id_2z"]')

                if isinstance(valor_informar, int):
                    valor_informar = str(valor_informar) + ",00"

                elif isinstance(valor_informar, float):
                    valor_informar = f"{valor_informar:.2f}".replace(".", ",")

                campo_valor_dml.send_keys(valor_informar)

                id_campo_valor_dml = campo_valor_dml.get_attribute("id")
                self.driver.execute_script(
                    f"document.getElementById('{id_campo_valor_dml}').blur()",
                )
                self.interact.sleep_load('div[id="j_id_2z"]')

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise e

    def set_risk(self) -> None:
        """Set the risk type for the provision.

        Raises:
            None

        """
        self.driver.execute_script(
            'document.getElementById("j_id_2z:j_id_32_2e:processoAmountObjetoDt").style.zoom = "0.5" ',
        )
        try:
            self.message = "Alterando risco"
            self.type_log = "log"
            self.prt()

            row_valores = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "tbody[id='j_id_2z:j_id_32_2e:processoAmountObjetoDt_data']",
                )),
            ).find_elements(
                By.XPATH,
                './/tr[contains(@class, "ui-datatable-odd") or contains(@class, "ui-datatable-even")]',
            )

            # def filter_risk(x: WebElement) -> bool:
            #     td_values = x.find_elements(By.TAG_NAME, "td")
            #     input_values = td_values[9].find_element(By.CSS_SELECTOR, 'input[id*="_input"]')
            #     value_attribute = input_values.get_attribute("value")

            #     return value_attribute is not None and value_attribute != ""

            # selector_filter_risk = list(
            #     filter(
            #         filter_risk,
            #         row_valores,
            #     )
            # )

            for row_risk in row_valores:
                selector_filter_risk = (
                    row_risk.find_elements(By.TAG_NAME, "td")[10]
                    .find_element(By.TAG_NAME, "div")
                    .find_element(By.TAG_NAME, "select")
                )

                id_selector = selector_filter_risk.get_attribute("id")
                css_selector_filter_risk = f'select[id="{id_selector}"]'

                provisao_from_xlsx = (
                    str(self.bot_data.get("PROVISAO"))
                    .lower()
                    .replace("possivel", "possível")
                    .replace("provavel", "provável")
                )

                self.interact.select2_elaw(
                    css_selector_filter_risk,
                    provisao_from_xlsx,
                )

                self.interact.sleep_load('div[id="j_id_3c"]')

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise e

    def informar_datas(self) -> None:
        """Inform the correction base date and interest date.

        Raises:
            None

        """
        try:
            self.message = "Alterando datas de correção base e juros"
            self.type_log = "log"
            self.prt()

            def set_data_correcao(data_base_correcao: str) -> None:
                data_correcao = self.driver.find_element(
                    By.CSS_SELECTOR,
                    self.elements.data_correcaoCss,
                )
                css_daata_correcao = data_correcao.get_attribute("id")
                self.interact.clear(data_correcao)
                self.interact.send_key(data_correcao, data_base_correcao)

                self.driver.execute_script(
                    f"document.getElementById('{css_daata_correcao}').blur()",
                )
                self.interact.sleep_load('div[id="j_id_2z"]')

            def set_data_juros(data_base_juros: str) -> None:
                data_juros = self.driver.find_element(
                    By.CSS_SELECTOR,
                    self.elements.data_jurosCss,
                )
                css_data = data_juros.get_attribute("id")
                self.interact.clear(data_juros)
                self.interact.send_key(data_juros, data_base_juros)
                self.driver.execute_script(
                    f"document.getElementById('{css_data}').blur()",
                )
                self.interact.sleep_load('div[id="j_id_2z"]')

            data_base_correcao = self.bot_data.get("DATA_BASE_CORRECAO")
            data_base_juros = self.bot_data.get("DATA_BASE_JUROS")
            if data_base_correcao is not None:
                if isinstance(data_base_correcao, datetime):
                    data_base_correcao = data_base_correcao.strftime("%d/%m/%Y")

                set_data_correcao(data_base_correcao)

            if data_base_juros is not None:
                if isinstance(data_base_juros, datetime):
                    data_base_juros = data_base_juros.strftime("%d/%m/%Y")

                set_data_juros(data_base_juros)

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise e

    def informar_motivo(self) -> None:
        """Inform the justification for the provision.

        Raises:
            None

        """
        try:
            try_salvar = self.driver.find_element(
                By.CSS_SELECTOR,
                self.elements.botao_salvar_id,
            )

            sleep(1)
            try_salvar.click()

            self.interact.sleep_load('div[id="j_id_2z"]')

            self.message = "Informando justificativa"
            self.type_log = "log"
            self.prt()
            informar_motivo: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.texto_motivo,
                )),
            )
            informar_motivo.send_keys(
                self.bot_data.get("OBSERVACAO", "Atualização de provisão"),
            )
            id_informar_motivo = informar_motivo.get_attribute("id")
            self.driver.execute_script(
                f"document.getElementById('{id_informar_motivo}').blur()",
            )

        except Exception as e:
            # TODO(Nicholas Silva): Criação de Exceptions
            # https://github.com/REM-Infotech/CrawJUD-Reestruturado/issues/35
            self.logger.exception("".join(traceback.format_exception(e)))
            raise e

    def save_changes(self) -> None:
        """Save all changes made during the provision process.

        Raises:
            ExecutionError: If unable to save the provision.

        """
        self.interact.sleep_load('div[id="j_id_2z"]')
        salvar = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.botao_salvar_id,
        )
        salvar.click()

        check_provisao_atualizada = None
        with suppress(TimeoutException):
            check_provisao_atualizada: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "#valoresGeralPanel_header > span",
                )),
            )

        if not check_provisao_atualizada:
            raise ExecutionError(message="Não foi possivel atualizar provisão")

        comprovante = self.print_comprovante()
        data = [
            str(self.bot_data.get("NUMERO_PROCESSO")),
            comprovante,
            "Provisão atualizada com sucesso!",
        ]
        self.append_success(data, message="Provisão atualizada com sucesso!")

    def print_comprovante(self) -> str:
        """Capture and save a screenshot as proof of the provision.

        Returns:
            str: The name of the saved screenshot file.

        """
        name_comprovante = f"Comprovante Cadastro - {self.bot_data.get('NUMERO_PROCESSO')} - PID {self.pid}.png"
        savecomprovante = (
            Path(self.output_dir_path).resolve().joinpath(name_comprovante)
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante
