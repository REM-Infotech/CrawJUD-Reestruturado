"""Module for managing new registrations in the ELAW system.

This module handles the creation and management of new registrations within the ELAW system.
It automates the process of entering new records and their associated data.

Classes:
    Cadastro: Manages new registrations by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

import time
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import CadastroParteError, SaveError
from crawjud.exceptions.elaw import AdvogadoError, ElawError

type_doc = {11: "cpf", 14: "cnpj"}


class Cadastro(CrawJUD):
    """The Cadastro class extends CrawJUD to manage registration tasks within the application.

    Attributes:
        type_doc (dict): A dictionary mapping document types to their identifiers.
        ...existing attributes...

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
        """Execute the main processing loop for registrations.

        Iterates over each entry in the data frame and processes it.
        Handles authentication and error logger.

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
        """Handle the registration queue processing.

        Refreshes the driver, extracts process information, and manages the registration
        process using the ELAW system. Logs the steps, calculates execution time,
        and handles potential exceptions.

        Raises:
            ExecutionError: If the process is not found or extraction fails.

        """
        try:
            self.bot_data = self.elawFormats(self.bot_data)
            search = self.search_bot.search(self.bot_data)

            if search is True:
                self.append_success([
                    self.bot_data.get("NUMERO_PROCESSO"),
                    "Processo já cadastrado!",
                    self.pid,
                ])

            elif search is not True:
                message = "Processo não encontrado, inicializando cadastro..."
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

                btn_newproc = self.driver.find_element(
                    By.CSS_SELECTOR, self.elements.botao_novo
                )
                btn_newproc.click()

                start_time = time.perf_counter()

                self.area_direito()
                self.subarea_direito()
                self.next_page()
                self.info_localizacao()
                self.informa_estado()
                self.informa_comarca()
                self.informa_foro()
                self.informa_vara()
                self.informa_proceso()
                self.informa_empresa()
                self.set_classe_empresa()
                self.parte_contraria()
                self.uf_proc()
                self.acao_proc()
                self.advogado_responsavel()
                self.adv_parte_contraria()
                self.data_distribuicao()
                self.info_valor_causa()
                self.escritorio_externo()
                self.tipo_contingencia()

                end_time = time.perf_counter()
                execution_time = end_time - start_time
                calc = execution_time / 60
                splitcalc = str(calc).split(".")
                minutes = int(splitcalc[0])
                seconds = int(float(f"0.{splitcalc[1]}") * 60)

                message = (
                    f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
                )
                type_log = "log"
                self.prt.print_msg(
                    message=message, pid=self.pid, row=self.row, type_log=type_log
                )

                self.salvar_tudo()

                if self.confirm_save() is True:
                    self.print_comprovante()

        except Exception as e:
            raise ElawError(
                exception=e, bot_execution_id=self.pid, message=str(e)
            ) from e

    def area_direito(self) -> None:
        """Select the area of law in the web form.

        This method interacts with a web form to select the area of law specified
        in the bot data. It logs the process and handles any necessary waits and
        interactions with the web elements.


        """
        message = "Informando área do direito"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        label_area: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_label_area,
            )),
            message="Erro ao encontrar elemento",
        )
        label_area.click()
        text = str(self.bot_data.get("AREA_DIREITO"))
        sleep(0.5)

        self.interact.select_item(self.elements.elemento, text)
        self.interact.sleep_load('div[id="j_id_3w"]')

        message = "Área do direito selecionada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def subarea_direito(self) -> None:
        """Select the sub-area of law in the web form.

        This method interacts with a web form to select the sub-area of law specified
        in the bot data. It logs the process and handles any necessary waits and
        interactions with the web elements.
        """
        message = "Informando sub-área do direito"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        expand_areasub: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.comboareasub_css,
            )),
            message="Erro ao encontrar elemento",
        )
        expand_areasub.click()
        text = str(self.bot_data.get("SUBAREA_DIREITO"))
        sleep(0.5)

        self.interact.select_item(self.elements.elemento_comboareasub, text)
        self.interact.sleep_load('div[id="j_id_3x"]')
        message = "Sub-Área do direito selecionada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def next_page(self) -> None:
        """Navigate to the next page by clicking the designated button.

        This method waits until the next page button is present in the DOM,
        then clicks it to navigate to the next page.

        """
        next_page: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_button,
            )),
            message="Erro ao encontrar elemento",
        )
        next_page.click()

    def info_localizacao(self) -> None:
        """Provide information about the location of the process.

        This method selects the judicial sphere of the process and logs the actions performed.
        It interacts with the web elements to set the sphere and waits for the loading to complete.

        """
        element_select = self.elements.css_esfera_judge
        text = "Judicial"

        message = "Informando esfera do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Esfera Informada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def informa_estado(self) -> None:
        """Informs the state of the process by selecting the appropriate option from a dropdown menu.

        This method retrieves the state information from the bot's data, logs the action,
        selects the state in the dropdown menu using the select2_elaw method, waits for the
        page to load, and then logs the completion of the action.


        """
        key = "ESTADO"
        element_select = self.elements.estado_input
        text = str(self.bot_data.get(key, None))

        message = "Informando estado do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Estado do processo informado!"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def informa_comarca(self) -> None:
        """Fill in the comarca (judicial district) information for the process.

        This method retrieves the comarca information from the bot data, selects the appropriate
        input element, and inputs the comarca text. It also logs the actions performed.
        Steps:
        1. Retrieve the comarca information from crawjud.bot data.
        2. Select the comarca input element.
        3. Log the action of informing the comarca.
        4. Use the select2_elaw method to input the comarca text.
        5. Wait for the loading indicator to disappear.
        6. Log the completion of the comarca information input.


        """
        text = str(self.bot_data.get("COMARCA"))
        element_select = self.elements.comarca_input

        message = "Informando comarca do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Comarca do processo informado!"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def informa_foro(self) -> None:
        """Informs the court jurisdiction (foro) for the process.

        This method retrieves the court jurisdiction information from the bot data,
        logs the action, and interacts with the web element to input the court jurisdiction.
        Steps:
        1. Retrieves the court jurisdiction from `self.bot_data`.
        2. Logs the action of informing the court jurisdiction.
        3. Uses the `select2_elaw` method to select the court jurisdiction in the web element.
        4. Waits for the loading element to disappear.
        5. Logs the completion of the action.


        """
        element_select = self.elements.foro_input
        text = str(self.bot_data.get("FORO"))

        message = "Informando foro do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Foro do processo informado!"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def informa_vara(self) -> None:
        """Fill in the court information for the process.

        This method retrieves the court information from the bot data and inputs it
        into the appropriate field in the ELAW system. It logs the actions performed
        and ensures the input is processed by the system.
        Steps:
        1. Retrieve the court information from `self.bot_data`.
        2. Log the action of informing the court information.
        3. Use the `select2_elaw` method to input the court information.
        4. Wait for the system to process the input.
        5. Log the completion of the action.



        """
        text = self.bot_data.get("VARA")
        element_select = self.elements.vara_input

        message = "Informando vara do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Vara do processo informado!"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def informa_proceso(self) -> None:
        """Inform the process number in the web form.

        This method retrieves the process number from the bot data, inputs it into the
        designated field, and handles any necessary interactions and waits.

        """
        key = "NUMERO_PROCESSO"
        css_campo_processo = self.elements.numero_processo

        message = "Informando número do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        campo_processo: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, css_campo_processo)),
            message="Erro ao encontrar elemento",
        )
        campo_processo.click()

        self.interact.send_key(campo_processo, self.bot_data.get(key))

        self.driver.execute_script(
            f'document.querySelector("{css_campo_processo}").blur()'
        )
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Número do processo informado!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def informa_empresa(self) -> None:
        """Inform the company associated with the process.

        This method retrieves the company name from the bot data, selects the appropriate
        input field, and inputs the company name. It includes logging of actions performed.



        """
        text = self.bot_data.get("EMPRESA")
        element_select = self.elements.empresa_input

        message = "Informando Empresa"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Empresa informada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def set_classe_empresa(self) -> None:
        """Set the classification of the company.

        This method retrieves the company type from the bot data, formats it,
        and uses it to interact with a specific input element on the page.
        It logs messages before and after the interaction to indicate the
        progress of the operation.



        """
        key = "TIPO_EMPRESA"
        element_select = self.elements.tipo_empresa_input
        text = self.bot_data.get(key).__str__().capitalize()

        message = "Informando classificação da Empresa"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Classificação da Empresa informada"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def parte_contraria(self) -> None:
        """Handle the opposing party information.

        This method manages the input and processing of opposing party details.
        It interacts with the relevant web elements and ensures the data is correctly
        entered and processed.

        Raises:
            ExecutionError: If an error occurs during the process.

        """
        message = "Preechendo informações da parte contrária"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        text = self.bot_data.get("TIPO_PARTE_CONTRARIA")
        element_select = self.elements.tipo_parte_contraria_input
        self.select2_elaw(element_select, text)

        table_tipo_doc: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_table_tipo_doc,
            )),
            message="Erro ao encontrar elemento",
        )
        table_tipo_doc = table_tipo_doc.find_elements(By.TAG_NAME, "td")
        self.interact.sleep_load('div[id="j_id_3x"]')

        for item in table_tipo_doc:
            item: WebElement = item
            get_label = str(item.find_element(By.TAG_NAME, "label").text).lower()
            tipo_doc = type_doc.get(
                len(
                    "".join(
                        filter(str.isdigit, self.bot_data.get("DOC_PARTE_CONTRARIA"))
                    )
                )
            )

            if get_label == tipo_doc:
                select_button = item.find_element(
                    By.CSS_SELECTOR, 'div[class="ui-radiobutton ui-widget"]'
                )
                select_button.click()
                break

        self.interact.sleep_load('div[id="j_id_3x"]')
        campo_doc: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_campo_doc,
            )),
            message="Erro ao encontrar elemento",
        )
        campo_doc.click()
        sleep(0.05)
        campo_doc.clear()
        sleep(0.05)
        self.interact.send_key(campo_doc, self.bot_data.get("DOC_PARTE_CONTRARIA"))
        self.interact.sleep_load('div[id="j_id_3x"]')

        search_button_parte: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_search_button,
            )),
            message="Erro ao encontrar elemento",
        )
        search_button_parte.click()
        self.interact.sleep_load('div[id="j_id_3x"]')

        check_parte = self.check_part_found(self.driver)

        if not check_parte:
            try:
                self.cad_parte()
                self.driver.switch_to.default_content()
                self.interact.sleep_load('div[id="j_id_3x"]')

            except Exception as e:
                raise CadastroParteError(
                    message="Não foi possível cadastrar parte",
                    exception=e,
                    bot_execution_id=self.pid,
                ) from e

        self.messsage = "Parte adicionada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def uf_proc(self) -> None:
        """Inform the federal unit (state) of the process.

        This method selects the appropriate state from the dropdown menu based on
        the bot data and logs the action performed.



        """
        get_div_select_locale: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_div_select_opt,
            )),
            message="Erro ao encontrar elemento",
        )
        get_div_select_locale.click()
        sleep(0.5)

        text = str(self.bot_data.get("CAPITAL_INTERIOR"))
        self.interact.select_item(self.elements.select_field, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        if str(self.bot_data.get("CAPITAL_INTERIOR")).lower() == "outro estado":
            other_location: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_other_location,
                )),
                message="Erro ao encontrar elemento",
            )
            other_location.click()
            self.interact.send_key(other_location, self.bot_data.get("ESTADO"))
            self.interact.send_key(other_location, Keys.ENTER)

    def acao_proc(self) -> None:
        """Inform the action of the process.

        This method selects the appropriate action type for the process from the
        dropdown menu based on the bot data and logs the action performed.



        """
        message = "Informando ação do processo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        div_comboProcessoTipo: WebElement = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.comboProcessoTipo,
            )),
            message="Erro ao encontrar elemento",
        )
        div_comboProcessoTipo.click()

        elemento = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.filtro_processo,
            )),
            message="Erro ao encontrar elemento",
        )

        text = self.bot_data.get("ACAO")
        self.interact.click(elemento)
        self.interact.send_key(elemento, text)
        self.interact.send_key(elemento, Keys.ENTER)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Ação informada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def data_distribuicao(self) -> None:
        """Inform the distribution date of the process.

        This method inputs the distribution date into the designated field and logs
        the action performed.



        """
        self.interact.sleep_load('div[id="j_id_3x"]')
        message = "Informando data de distribuição"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        self.interact.sleep_load('div[id="j_id_3x"]')
        data_distribuicao: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                self.elements.css_data_distribuicao,
            )),
            message="Erro ao encontrar elemento",
        )

        self.interact.clear(data_distribuicao)

        self.interact.send_key(
            data_distribuicao, self.bot_data.get("DATA_DISTRIBUICAO")
        )
        self.interact.send_key(data_distribuicao, Keys.TAB)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Data de distribuição informada!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def advogado_responsavel(self) -> None:
        """Inform the responsible lawyer for the process.

        This method retrieves the lawyer's information from the bot data, inputs it
        into the designated field, and logs the action performed.

        Raises:
            ExecutionError: If the lawyer is not found.

        """
        message = "informando advogado interno"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        input_adv_responsavel: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_adv_responsavel,
            )),
        )
        input_adv_responsavel.click()
        self.interact.send_key(
            input_adv_responsavel, self.bot_data.get("ADVOGADO_INTERNO")
        )

        css_wait_adv = r"#j_id_3k_1\:autoCompleteLawyer_panel > ul > li"

        wait_adv = None

        with suppress(TimeoutException):
            wait_adv: WebElement = WebDriverWait(self.driver, 25).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_wait_adv)),
            )

        if wait_adv:
            wait_adv.click()
        elif not wait_adv:
            raise AdvogadoError(
                message="Advogado interno não encontrado", bot_execution_id=self.pid
            )

        self.interact.sleep_load('div[id="j_id_3x"]')

        div_select_Adv: WebElement = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_div_select_Adv,
            )),
        )
        div_select_Adv.click()

        self.interact.sleep_load('div[id="j_id_3x"]')

        input_select_adv: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_input_select_Adv,
            )),
        )
        input_select_adv.click()

        self.interact.send_key(
            input_select_adv, self.bot_data.get("ADVOGADO_INTERNO")
        )
        input_select_adv.send_keys(Keys.ENTER)

        self.driver.execute_script(
            f"document.querySelector('{self.elements.css_div_select_Adv}').blur()"
        )

        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Advogado interno informado!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def adv_parte_contraria(self) -> None:
        """Inform the lawyer for the opposing party.

        This method retrieves the opposing party's lawyer information from the bot data,
        inputs it into the designated field, and logs the action performed.



        """
        message = "Informando Adv. Parte contrária"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        campo_adv: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_input_adv,
            )),
            message="Erro ao encontrar elemento",
        )
        campo_adv.click()
        campo_adv.clear()
        sleep(0.02)

        Text = str(self.bot_data.get("ADV_PARTE_CONTRARIA"))  # noqa: N806

        for i in ["\t", "\n"]:
            if i in Text:
                Text = Text.split(i)[0]  # noqa: N806
                break

        self.interact.send_key(campo_adv, Text)

        check_adv = None

        self.interact.sleep_load('div[id="j_id_3x"]')

        with suppress(TimeoutException):
            check_adv: WebElement = (
                WebDriverWait(self.driver, 15)
                .until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.css_check_adv,
                    )),
                    message="Erro ao encontrar elemento",
                )
                .text
            )
            self.interact.send_key(campo_adv, Keys.ENTER)
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_input_adv}').blur()"
            )

        if not check_adv:
            self.cad_adv()
            self.driver.switch_to.default_content()

        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Adv. parte contrária informado!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def info_valor_causa(self) -> None:
        """Inform the value of the cause.

        This method retrieves the cause value from the bot data, inputs it into the
        designated field, and logs the action performed.



        """
        message = "Informando valor da causa"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        valor_causa: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                self.elements.css_valor_causa,
            )),
            message="Erro ao encontrar elemento",
        )

        valor_causa.click()
        sleep(0.5)
        valor_causa.clear()

        self.interact.send_key(valor_causa, self.bot_data.get("VALOR_CAUSA"))
        self.driver.execute_script(
            f"document.querySelector('{self.elements.css_valor_causa}').blur()"
        )

        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Valor da causa informado!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def escritorio_externo(self) -> None:
        """Inform the external office involved in the process.

        This method retrieves the external office information from the bot data,
        inputs it into the designated field, and logs the action performed.



        """
        message = "Informando Escritório Externo"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        div_escritrorioexterno: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.escritrorio_externo,
            )),
            message="Erro ao encontrar elemento",
        )
        div_escritrorioexterno.click()
        sleep(1)

        text = self.bot_data.get("ESCRITORIO_EXTERNO")
        self.interact.select_item(self.elements.combo_escritorio, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Escritório externo informado!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def tipo_contingencia(self) -> None:
        """Inform the type of contingency for the process.

        This method selects the appropriate contingency type from the dropdown menu
        based on the bot data and logs the action performed.



        """
        message = "Informando contingenciamento"
        type_log = "log"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        element_select = self.elements.contingencia

        text = ["Passiva", "Passivo"]
        if str(self.bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        self.select2_elaw(element_select, text[0])
        self.interact.sleep_load('div[id="j_id_3x"]')

        element_select = self.elements.tipo_polo

        text = ["Passiva", "Passivo"]
        if str(self.bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        self.select2_elaw(element_select, text[1])
        self.interact.sleep_load('div[id="j_id_3x"]')

        message = "Contingenciamento informado!"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

    def cad_adv(self) -> None:
        """Register the lawyer information.

        This method handles the registration of lawyer details by interacting with
        the relevant web elements and logging the actions performed.

        Raises:
            ExecutionError: If an error occurs during the process.

        """
        try:
            message = "Cadastrando advogado"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

            add_parte: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_add_adv,
                )),
                message="Erro ao encontrar elemento",
            )
            add_parte.click()

            sleep(0.5)

            iframe: WebElement = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.XPATH, self.elements.xpath)),
                message="Erro ao encontrar elemento",
            )

            self.driver.switch_to.frame(iframe)

            sleep(0.5)

            naoinfomadoc: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_naoinfomadoc,
                )),
                message="Erro ao encontrar elemento",
            )
            naoinfomadoc.click()

            """ CORRIGIR """
            # sleep(0.5)
            # continuebutton: WebElement = self.wait.until(
            #     ec.presence_of_element_located(
            #         (By.CSS_SELECTOR, self.elements.bota_continuar)
            #     ),
            #     message="Erro ao encontrar elemento",
            # )
            # continuebutton.click()

            # sleep(0.5)
            """ CORRIGIR """

            sleep(0.5)
            continuebutton: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.botao_continuar,
                )),
                message="Erro ao encontrar elemento",
            )
            continuebutton.click()

            sleep(0.5)

            input_nomeadv: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_input_nomeadv,
                )),
                message="Erro ao encontrar elemento",
            )
            input_nomeadv.click()
            self.interact.send_key(
                input_nomeadv, self.bot_data.get("ADV_PARTE_CONTRARIA")
            )

            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_input_nomeadv}').blur()"
            )

            sleep(0.05)
            salvar: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.salvarcss,
                )),
                message="Erro ao encontrar elemento",
            )
            salvar.click()

            message = "Advogado cadastrado!"
            type_log = "info"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            self.interact.sleep_load('div[id="j_id_3x"]')

        except Exception as e:
            raise AdvogadoError(
                message="Não foi possível cadastrar advogado",
                exception=e,
                bot_execution_id=self.pid,
            ) from e

    def cad_parte(self) -> None:
        """Register the party information.

        This method handles the registration of party details by interacting with
        the relevant web elements and logging the actions performed.

        Raises:
            ExecutionError: If an error occurs during the process

        """
        try:
            message = "Cadastrando parte"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

            add_parte: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.parte_contraria,
                )),
                message="Erro ao encontrar elemento",
            )
            add_parte.click()

            self.interact.sleep_load('div[id="j_id_3x"]')

            iframe = None

            iframe: WebElement = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.XPATH,
                    self.elements.xpath_iframe,
                )),
                message="Erro ao encontrar elemento",
            )

            self.driver.switch_to.frame(iframe)

            with suppress(TimeoutException, NoSuchElementException):
                set_infomar_cpf: WebElement = (
                    self.wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            self.elements.cpf_cnpj,
                        )),
                        message="Erro ao encontrar elemento",
                    )
                    .find_elements(By.TAG_NAME, "td")[1]
                    .find_elements(By.CSS_SELECTOR, self.elements.botao_radio_widget)[
                        1
                    ]
                )

                set_infomar_cpf.click()

            table_tipo_doc: WebElement = WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.tipo_cpf_cnpj,
                )),
                message="Erro ao encontrar elemento",
            )
            itensintotable = table_tipo_doc.find_elements(By.TAG_NAME, "td")

            sleep(0.5)

            for item in itensintotable:
                check_tipo = item.find_element(By.TAG_NAME, "label").text

                numero = "".join(
                    filter(str.isdigit, self.bot_data.get("DOC_PARTE_CONTRARIA"))
                )

                if len(numero) == 11:
                    tipo_doc = "cpf"

                elif len(numero) == 14:
                    tipo_doc = "cnpj"

                if check_tipo.lower() == tipo_doc:
                    select_tipo = item.find_element(
                        By.CSS_SELECTOR, self.elements.botao_radio_widget
                    )
                    sleep(0.5)
                    select_tipo.click()
                    break

            self.interact.sleep_load('div[id="j_id_3x"]')

            if tipo_doc == "cpf":
                css_input_doc = self.elements.tipo_cpf

            elif tipo_doc == "cnpj":
                css_input_doc = self.elements.tipo_cnpj

            input_doc: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_input_doc)),
                message="Erro ao encontrar elemento",
            )
            input_doc.click()
            sleep(0.05)
            input_doc.clear()
            self.interact.send_key(
                input_doc, self.bot_data.get("DOC_PARTE_CONTRARIA")
            )
            continuar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.botao_parte_contraria
            )
            continuar.click()

            self.interact.sleep_load('div[id="j_id_3x"]')
            name_parte: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_name_parte,
                )),
                message="Erro ao encontrar elemento",
            )
            name_parte.click()
            sleep(0.05)
            self.interact.send_key(
                name_parte, self.bot_data.get("PARTE_CONTRARIA").__str__().upper()
            )
            self.driver.execute_script(
                f"document.querySelector('{self.elements.css_name_parte}').blur()"
            )

            save_parte: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.css_save_button,
                )),
                message="Erro ao encontrar elemento",
            )
            save_parte.click()

            message = "Parte cadastrada!"
            type_log = "info"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )

        except Exception as e:
            raise CadastroParteError(exception=e, bot_execution_id=self.pid) from e

    def salvar_tudo(self) -> None:
        """Save all entered information.

        This method clicks the save button to persist all entered data and logs the
        action performed.



        """
        self.interact.sleep_load('div[id="j_id_3x"]')
        salvartudo: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_salvar_proc,
            )),
            message="Erro ao encontrar elemento",
        )

        message = "Salvando processo novo"
        type_log = "info"
        self.prt.print_msg(
            message=message, pid=self.pid, row=self.row, type_log=type_log
        )

        salvartudo.click()

    def print_comprovante(self) -> None:
        """Print the receipt of the registration.

        This method handles the printing of the registration receipt by interacting
        with the relevant web elements, taking a screenshot, and logging the actions
        performed.



        """
        name_comprovante = f"Comprovante Cadastro - {self.bot_data.get('NUMERO_PROCESSO')} - PID {self.pid}.png"
        savecomprovante = (
            Path(self.output_dir_path).resolve().joinpath(name_comprovante)
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        self.append_success([
            self.bot_data.get("NUMERO_PROCESSO"),
            name_comprovante,
            self.pid,
        ])

    def check_part_found(self, driver: WebDriver) -> str | None:
        """Check if the opposing party is found.

        This method verifies the presence of the opposing party in the process.
        It interacts with the web elements to perform the check and returns the result.

        Args:
            driver: The WebDriver instance.

        Returns:
            str | None: The status of the opposing party search.

        """
        name_parte = ""
        with suppress(NoSuchElementException):
            name_parte = (
                self.driver.find_element(By.CSS_SELECTOR, self.elements.css_t_found)
                .find_element(By.TAG_NAME, "td")
                .text
            )

        if name_parte != "":
            return name_parte

        return None

    def confirm_save(self) -> bool:
        """Confirm the saving of information.

        This method verifies that all information has been successfully saved
        by checking the URL and interacting with web elements as needed.
        Logs the action performed.

        Returns:
            bool: True if the save is confirmed, False otherwise.

        Raises:
            ExecutionError: If the save confirmation fails.

        """
        wait_confirm_save = None

        with suppress(TimeoutException):
            wait_confirm_save: WebElement = WebDriverWait(self.driver, 20).until(
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
                message="Erro ao encontrar elemento",
            )

        if wait_confirm_save:
            message = "Processo salvo com sucesso!"
            type_log = "log"
            self.prt.print_msg(
                message=message, pid=self.pid, row=self.row, type_log=type_log
            )
            return True

        if not wait_confirm_save:
            erro_elaw: WebElement | str = None
            with suppress(TimeoutException, NoSuchElementException):
                erro_elaw = (
                    self.wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            self.elements.div_messageerro_css,
                        )),
                        message="Erro ao encontrar elemento",
                    )
                    .find_element(By.TAG_NAME, "ul")
                    .text
                )

            if not erro_elaw:
                erro_elaw = (
                    "Cadastro do processo nao finalizado, verificar manualmente"
                )

            raise SaveError(message=erro_elaw, bot_execution_id=self.pid)
