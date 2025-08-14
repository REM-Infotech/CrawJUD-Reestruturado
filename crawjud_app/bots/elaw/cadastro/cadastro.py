"""Module for managing new registrations in the ELAW system.

This module handles the creation and management of new registrations within the ELAW system.
It automates the process of entering new records and their associated data.

Classes:
    Cadastro: Manages new registrations by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)

"""

import traceback
from contextlib import suppress
from pathlib import Path
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from controllers.bots.master.bot_head import ClassBot
from crawjud_app.common.exceptions.bot import ExecutionError

type_doc = {"11": "cpf", "14": "cnpj"}

ELEMENT_LOAD = 'div[id="j_id_48"]'


class PreCadastro(ClassBot):
    def area_direito(self) -> None:
        wait = self.wait
        self.message = "Informando área do direito"
        self.type_log = "log"
        self.prt()
        text = str(self.bot_data.get("AREA_DIREITO"))
        sleep(0.5)

        element_area_direito = wait.until(
            ec.presence_of_element_located((By.XPATH, self.elements.css_label_area)),
        )
        self.select2_elaw(element_area_direito, text)
        self.interact.sleep_load('div[id="j_id_47"]')

        self.message = "Área do direito selecionada!"
        self.type_log = "info"
        self.prt()

    def subarea_direito(self) -> None:
        wait = self.wait
        self.message = "Informando sub-área do direito"
        self.type_log = "log"
        self.prt()

        text = str(self.bot_data.get("SUBAREA_DIREITO"))
        sleep(0.5)

        element_subarea = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                self.elements.comboareasub_css,
            )),
        )
        self.select2_elaw(element_subarea, text)

        self.interact.sleep_load()
        self.message = "Sub-Área do direito selecionada!"
        self.type_log = "info"
        self.prt()

    def next_page(self) -> None:
        next_page: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_button,
            )),
            message="Erro ao encontrar elemento",
        )
        next_page.click()

    def info_localizacao(self) -> None:
        element_select = self.elements.css_esfera_judge
        text = "Judicial"

        self.message = "Informando esfera do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Esfera Informada!"
        self.type_log = "info"
        self.prt()

    def estado(self) -> None:
        """Informs the state of the process by selecting the appropriate option from a dropdown menu.

        This method retrieves the state information from the bot's data, logs the action,
        selects the state in the dropdown menu using the select2_elaw method, waits for the
        page to load, and then logs the completion of the action.


        """
        key = "ESTADO"
        element_select = self.elements.estado_input
        text = str(self.bot_data.get(key, None))

        self.message = "Informando estado do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Estado do processo informado!"
        self.type_log = "log"
        self.prt()

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

        self.message = "Informando comarca do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Comarca do processo informado!"
        self.type_log = "log"
        self.prt()

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

        self.message = "Informando foro do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Foro do processo informado!"
        self.type_log = "log"
        self.prt()

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

        self.message = "Informando vara do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Vara do processo informado!"
        self.type_log = "log"
        self.prt()

    def informa_proceso(self) -> None:
        """Inform the process number in the web form.

        This method retrieves the process number from the bot data, inputs it into the
        designated field, and handles any necessary interactions and waits.

        """
        key = "NUMERO_PROCESSO"
        css_campo_processo = self.elements.numero_processo

        self.message = "Informando número do processo"
        self.type_log = "log"
        self.prt()

        campo_processo: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, css_campo_processo)),
            message="Erro ao encontrar elemento",
        )
        campo_processo.click()

        self.interact.send_key(campo_processo, self.bot_data.get(key))

        self.driver.execute_script(
            f'document.querySelector("{css_campo_processo}").blur()',
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Número do processo informado!"
        self.type_log = "info"
        self.prt()

    def informa_empresa(self) -> None:
        """Inform the company associated with the process.

        This method retrieves the company name from the bot data, selects the appropriate
        input field, and inputs the company name. It includes logging of actions performed.



        """
        text = self.bot_data.get("EMPRESA")
        element_select = self.elements.empresa_input

        self.message = "Informando Empresa"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Empresa informada!"
        self.type_log = "info"
        self.prt()

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

        self.message = "Informando classificação da Empresa"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Classificação da Empresa informada"
        self.type_log = "info"
        self.prt()

    def parte_contraria(self) -> None:
        """Handle the opposing party information.

        This method manages the input and processing of opposing party details.
        It interacts with the relevant web elements and ensures the data is correctly
        entered and processed.

        Raises:
            ExecutionError: If an error occurs during the process.

        """
        self.message = "Preechendo informações da parte contrária"
        self.type_log = "log"
        self.prt()

        text = self.bot_data.get("TIPO_PARTE_CONTRARIA")
        element_select = self.elements.tipo_parte_contraria_input
        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )

        doc_to_list = list(
            filter(
                lambda x: str.isdigit(x),
                ",".join(self.bot_data.get("DOC_PARTE_CONTRARIA")).split(","),
            ),
        )
        tipo_doc = type_doc.get(str(len(doc_to_list)))
        select_tipo_doc = self.elements.select_tipo_doc
        self.select2_elaw(select_tipo_doc, tipo_doc)

        self.interact.sleep_load(ELEMENT_LOAD)
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
        self.interact.sleep_load(ELEMENT_LOAD)

        search_button_parte: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_search_button,
            )),
            message="Erro ao encontrar elemento",
        )
        search_button_parte.click()
        self.interact.sleep_load(ELEMENT_LOAD)

        check_parte = self.check_part_found()

        if not check_parte:
            try:
                self.cadastro_parte_contraria()
                self.driver.switch_to.default_content()
                self.interact.sleep_load(ELEMENT_LOAD)

            except Exception as e:
                self.logger.exception("".join(traceback.format_exception(e)))
                raise ExecutionError(
                    message="Não foi possível cadastrar parte",
                    e=e,
                ) from e

        self.messsage = "Parte adicionada!"
        self.type_log = "info"
        self.prt()

    def uf_proc(self) -> None:
        """Inform the federal unit (state) of the process.

        This method selects the appropriate state from the dropdown menu based on
        the bot data and logs the action performed.



        """
        self.message = "Preenchendo UF Processo..."
        self.type_log = "log"
        self.prt()
        element_select = self.elements.select_uf_proc
        text = str(self.bot_data.get("CAPITAL_INTERIOR"))
        self.select2_elaw(self.driver.find_element(By.XPATH, element_select), text)
        sleep(0.5)

        self.interact.sleep_load(ELEMENT_LOAD)

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
        self.message = "Informando ação do processo"
        self.type_log = "log"
        self.prt()

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
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Ação informada!"
        self.type_log = "info"
        self.prt()

    def data_distribuicao(self) -> None:
        """Inform the distribution date of the process.

        This method inputs the distribution date into the designated field and logs
        the action performed.



        """
        self.interact.sleep_load(ELEMENT_LOAD)
        self.message = "Informando data de distribuição"
        self.type_log = "log"
        self.prt()

        self.interact.sleep_load(ELEMENT_LOAD)
        data_distribuicao: WebElement = self.wait.until(
            ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                self.elements.css_data_distribuicao,
            )),
            message="Erro ao encontrar elemento",
        )

        self.interact.clear(data_distribuicao)

        self.interact.send_key(
            data_distribuicao,
            self.bot_data.get("DATA_DISTRIBUICAO"),
        )
        self.interact.send_key(data_distribuicao, Keys.TAB)
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Data de distribuição informada!"
        self.type_log = "info"
        self.prt()

    def advogado_interno(self) -> None:
        interact = self.interact
        wait = self.wait
        driver = self.driver
        elements = self.elements
        bot_data = self.bot_data
        select2_elaw = self.select2_elaw
        prt = self.prt

        self.message = "informando advogado interno"
        self.type_log = "log"
        prt()

        input_adv_responsavel: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, elements.adv_responsavel)),
        )
        input_adv_responsavel.click()
        interact.send_key(input_adv_responsavel, bot_data.get("ADVOGADO_INTERNO"))

        id_input_adv = input_adv_responsavel.get_attribute("id").replace(
            "_input",
            "_panel",
        )
        css_wait_adv = f"span[id='{id_input_adv}'] > ul > li"

        wait_adv = None

        with suppress(TimeoutException):
            wait_adv: WebElement = WebDriverWait(driver, 25).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_wait_adv)),
            )

        if wait_adv:
            wait_adv.click()
        elif not wait_adv:
            raise ExecutionError(message="Advogado interno não encontrado")

        interact.sleep_load(ELEMENT_LOAD)

        interact.sleep_load(ELEMENT_LOAD)
        element_select = wait.until(
            ec.presence_of_element_located((
                By.XPATH,
                elements.select_advogado_responsavel,
            )),
        )
        select2_elaw(element_select, bot_data.get("ADVOGADO_INTERNO"))

        id_element = element_select.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        driver.execute_script(comando)

        interact.sleep_load(ELEMENT_LOAD)

        self.message = "Advogado interno informado!"
        self.type_log = "info"
        prt()

    def adv_parte_contraria(self) -> None:
        """Inform the lawyer for the opposing party.

        This method retrieves the opposing party's lawyer information from the bot data,
        inputs it into the designated field, and logs the action performed.

        """
        driver = self.driver
        wait = self.wait
        elements = self.elements
        interact = self.interact
        prt = self.prt
        bot_data = self.bot_data
        self.message = "Informando Adv. Parte contrária"
        self.type_log = "log"

        campo_adv: WebElement = wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, elements.css_input_adv)),
            message="Erro ao encontrar elemento",
        )
        campo_adv.click()
        campo_adv.clear()
        sleep(0.02)

        text = str(bot_data.get("ADV_PARTE_CONTRARIA"))

        for i in ["\t", "\n"]:
            if i in text:
                text = text.split(i)[0]
                break

        interact.send_key(campo_adv, text)

        check_adv = None

        interact.sleep_load(ELEMENT_LOAD)

        with suppress(TimeoutException):
            check_adv: WebElement = (
                WebDriverWait(driver, 15)
                .until(
                    ec.presence_of_element_located((
                        By.XPATH,
                        elements.css_check_adv,
                    )),
                    message="Erro ao encontrar elemento",
                )
                .text
            )
            interact.send_key(campo_adv, Keys.ENTER)
            driver.execute_script(
                f"document.querySelector('{elements.css_input_adv}').blur()",
            )

        if not check_adv:
            self.cadastro_advogado_contra()
            driver.switch_to.default_content()

        interact.sleep_load(ELEMENT_LOAD)

        self.message = "Adv. parte contrária informado!"
        self.type_log = "info"
        prt()

    def info_valor_causa(self) -> None:
        """Inform the value of the cause.

        This method retrieves the cause value from the bot data, inputs it into the
        designated field, and logs the action performed.



        """
        prt = self.prt
        wait = self.wait
        driver = self.driver
        interact = self.interact
        bot_data = self.bot_data
        elements = self.elements

        self.message = "Informando valor da causa"
        self.type_log = "log"
        prt()

        valor_causa: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, elements.valor_causa)),
            message="Erro ao encontrar elemento",
        )

        valor_causa.click()
        sleep(0.5)
        valor_causa.clear()
        id_valor_causa = valor_causa.get_attribute("id")
        input_valor_causa = f'input[id="{id_valor_causa}"]'
        interact.send_key(valor_causa, bot_data.get("VALOR_CAUSA"))

        driver.execute_script(f"document.querySelector('{input_valor_causa}').blur()")

        interact.sleep_load(ELEMENT_LOAD)

        self.message = "Valor da causa informado!"
        self.type_log = "info"
        prt()

    def escritorio_externo(self) -> None:
        """Inform the external office involved in the process.

        This method retrieves the external office information from the bot data,
        inputs it into the designated field, and logs the action performed.



        """
        prt = self.prt
        wait = self.wait
        bot_data = self.bot_data
        interact = self.interact
        elements = self.elements
        self.message = "Informando Escritório Externo"
        self.type_log = "log"
        prt()

        div_escritrorioexterno: WebElement = wait.until(
            ec.presence_of_element_located((By.XPATH, elements.escritrorio_externo)),
            message="Erro ao encontrar elemento",
        )
        div_escritrorioexterno.click()
        sleep(1)

        text = bot_data.get("ESCRITORIO_EXTERNO")
        select_escritorio = wait.until(
            ec.presence_of_element_located((By.XPATH, elements.select_escritorio)),
        )
        interact.select2_elaw(select_escritorio, text)
        interact.sleep_load(ELEMENT_LOAD)

        self.message = "Escritório externo informado!"
        self.type_log = "info"
        prt()

    def tipo_contingencia(self) -> None:
        """Inform the type of contingency for the process.

        This method selects the appropriate contingency type from the dropdown menu
        based on the bot data and logs the action performed.



        """
        prt = self.prt
        wait = self.wait
        bot_data = self.bot_data
        interact = self.interact
        elements = self.elements
        select2_elaw = self.select2_elaw

        self.message = "Informando contingenciamento"
        self.type_log = "log"
        prt()

        text = ["Passiva", "Passivo"]
        if str(bot_data.get("TIPO_EMPRESA")).lower() == "autor":
            text = ["Ativa", "Ativo"]

        select_contigencia = wait.until(
            ec.presence_of_element_located((By.XPATH, elements.contingencia)),
        )
        select_polo = wait.until(
            ec.presence_of_element_located((By.XPATH, elements.tipo_polo)),
        )

        select2_elaw(select_contigencia, text[0])
        interact.sleep_load(ELEMENT_LOAD)

        select2_elaw(select_polo, text[1])
        interact.sleep_load(ELEMENT_LOAD)

        self.message = "Contingenciamento informado!"
        self.type_log = "info"
        prt()

    def cadastro_advogado_contra(self) -> None:
        """Register the lawyer information.

        This method handles the registration of lawyer details by interacting with
        the relevant web elements and logging the actions performed.

        Raises:
            ExecutionError: If an error occurs during the process.

        """
        try:
            wait = self.wait
            driver = self.driver
            elements = self.elements
            interact = self.interact
            bot_data = self.bot_data
            # select2_elaw = self.select2_elaw
            prt = self.prt
            self.message = "Cadastrando advogado"
            self.type_log = "log"
            prt()

            add_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.XPATH,
                    elements.btn_novo_advogado_contra,
                )),
                message="Erro ao encontrar elemento",
            )
            add_parte.click()

            interact.sleep_load(ELEMENT_LOAD)

            main_window = driver.current_window_handle

            iframe: WebElement = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.iframe_cadastro_advogado_contra,
                )),
                message="Erro ao encontrar elemento",
            )
            link_iframe = iframe.get_attribute("src")
            driver.switch_to.new_window("tab")
            driver.get(link_iframe)

            sleep(0.5)

            naoinfomadoc: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.css_naoinfomadoc,
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
            continuebutton: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.botao_continuar,
                )),
                message="Erro ao encontrar elemento",
            )
            continuebutton.click()

            interact.sleep_load('div[id="j_id_1o"]')
            sleep(0.5)

            input_nomeadv: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.css_input_nomeadv,
                )),
                message="Erro ao encontrar elemento",
            )
            input_nomeadv.click()
            interact.send_key(input_nomeadv, bot_data.get("ADV_PARTE_CONTRARIA"))

            driver.execute_script(
                f"document.querySelector('{elements.css_input_nomeadv}').blur()",
            )

            sleep(0.05)
            salvar: WebElement = wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, elements.salvarcss)),
                message="Erro ao encontrar elemento",
            )
            salvar.click()

            self.message = "Advogado cadastrado!"
            self.type_log = "info"
            prt()

            driver.close()
            driver.switch_to.window(main_window)

            wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.iframe_cadastro_advogado_close_dnv,
                )),
            )

            interact.sleep_load(ELEMENT_LOAD)

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(
                message="Não foi possível cadastrar advogado",
                e=e,
            ) from e

    def cadastro_parte_contraria(self) -> None:
        """Register the party information.

        This method handles the registration of party details by interacting with
        the relevant web elements and logging the actions performed.

        Raises:
            ExecutionError: If an error occurs during the process

        """
        try:
            prt = self.prt
            logger = self.logger
            self.message = "Cadastrando parte"
            self.type_log = "log"
            prt()

            wait = self.wait
            driver = self.driver
            elements = self.elements
            interact = self.interact
            bot_data = self.bot_data
            select2_elaw = self.select2_elaw

            add_parte: WebElement = wait.until(
                ec.presence_of_element_located((By.XPATH, elements.parte_contraria)),
                message="Erro ao encontrar elemento",
            )
            add_parte.click()

            interact.sleep_load(ELEMENT_LOAD)

            iframe = None

            main_window = driver.current_window_handle

            iframe: WebElement = WebDriverWait(driver, 10).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.iframe_cadastro_parte_contraria,
                )),
                message="Erro ao encontrar elemento",
            )
            link_iframe = iframe.get_attribute("src")
            driver.switch_to.new_window("tab")
            driver.get(link_iframe)
            sleep(0.5)
            with suppress(TimeoutException, NoSuchElementException):
                set_infomar_cpf: WebElement = (
                    wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            elements.cpf_cnpj,
                        )),
                        message="Erro ao encontrar elemento",
                    )
                    .find_elements(By.TAG_NAME, "td")[1]
                    .find_elements(By.CSS_SELECTOR, elements.botao_radio_widget)[1]
                )

                set_infomar_cpf.click()

            interact.sleep_load('div[id="j_id_1o"]')
            doc_to_list = list(
                filter(
                    lambda x: str.isdigit(x),
                    ",".join(bot_data.get("DOC_PARTE_CONTRARIA")).split(","),
                ),
            )
            tipo_doc = type_doc.get(str(len(doc_to_list)), "cpf")
            select_tipo_doc = elements.tipo_cpf_cnpj
            element_select = wait.until(
                ec.presence_of_element_located((By.XPATH, select_tipo_doc)),
            )
            select2_elaw(element_select, tipo_doc.upper())

            sleep(2)
            interact.sleep_load('div[id="j_id_1o"]')

            css_input_doc = elements.tipo_cpf
            if tipo_doc == "cnpj":
                css_input_doc = elements.tipo_cnpj

            input_doc: WebElement = wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_input_doc)),
                message="Erro ao encontrar elemento",
            )
            input_doc.click()
            sleep(0.05)
            input_doc.clear()
            interact.send_key(input_doc, bot_data.get("DOC_PARTE_CONTRARIA"))
            continuar = driver.find_element(
                By.CSS_SELECTOR,
                elements.botao_parte_contraria,
            )
            continuar.click()

            interact.sleep_load('div[id="j_id_1o"]')
            name_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.css_name_parte,
                )),
                message="Erro ao encontrar elemento",
            )
            name_parte.click()
            sleep(0.05)
            interact.send_key(
                name_parte,
                bot_data.get("PARTE_CONTRARIA").__str__().upper(),
            )
            driver.execute_script(
                f"document.querySelector('{elements.css_name_parte}').blur()",
            )

            save_parte: WebElement = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    elements.css_save_button,
                )),
                message="Erro ao encontrar elemento",
            )
            save_parte.click()

            self.message = "Parte cadastrada!"
            self.type_log = "info"
            prt()
            driver.close()

            driver.switch_to.window(main_window)

            element_close = elements.iframe_cadastro_parte_close_dnv
            wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, element_close)),
            ).click()

        except Exception as e:
            logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def salvar_tudo(self) -> None:
        """Save all entered information.

        This method clicks the save button to persist all entered data and logs the
        action performed.



        """
        wait = self.wait
        elements = self.elements
        interact = self.interact
        interact.sleep_load(ELEMENT_LOAD)
        salvartudo: WebElement = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                elements.css_salvar_proc,
            )),
            message="Erro ao encontrar elemento",
        )

        self.message = "Salvando processo novo"
        self.type_log = "info"
        self.prt()

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

    def check_part_found(self) -> str | None:
        """Check if the opposing party is found.

        This method verifies the presence of the opposing party in the process.
        It interacts with the web elements to perform the check and returns the result.

        Args:
            driver: The WebDriver instance.

        Returns:
            str | None: The status of the opposing party search.

        """
        name_parte = None
        tries: int = 0

        driver = self.driver
        elements = self.elements
        while tries < 4:
            with suppress(NoSuchElementException):
                name_parte = (
                    driver.find_element(
                        By.CSS_SELECTOR,
                        elements.css_t_found,
                    )
                    .find_element(By.TAG_NAME, "td")
                    .text
                )

            if name_parte:
                break

            sleep(1)
            tries += 1

        return name_parte

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
        prt = self.prt
        wait = self.wait
        driver = self.driver
        elements = self.elements
        wait_confirm_save = None

        with suppress(TimeoutException):
            wait_confirm_save: WebElement = WebDriverWait(driver, 20).until(
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
                message="Erro ao encontrar elemento",
            )

        if wait_confirm_save:
            self.message = "Processo salvo com sucesso!"
            self.type_log = "log"
            prt()
            return True

        if not wait_confirm_save:
            mensagem_erro: str = None
            with suppress(TimeoutException, NoSuchElementException):
                mensagem_erro = (
                    wait.until(
                        ec.presence_of_element_located((
                            By.CSS_SELECTOR,
                            elements.div_messageerro_css,
                        )),
                        message="Erro ao encontrar elemento",
                    )
                    .find_element(By.TAG_NAME, "ul")
                    .text
                )

            if not mensagem_erro:
                mensagem_erro = (
                    "Cadastro do processo nao finalizado, verificar manualmente"
                )

            raise ExecutionError(mensagem_erro)
