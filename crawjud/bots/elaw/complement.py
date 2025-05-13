"""Module for managing registration completion tasks in the ELAW system.

This module handles the completion and supplementation of registration data within the ELAW
system. It automates the process of filling in missing or additional registration details.

Classes:
    Complement: Manages registration completion by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)
    campos_validar (list): Fields to validate during registration completion

"""

import time
import traceback
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Callable, Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.core import CrawJUD
from crawjud.exceptions.bot import ExecutionError

type_doc = {11: "cpf", 14: "cnpj"}

campos_validar: list[str] = [
    "estado",
    "comarca",
    "foro",
    "vara",
    "divisao",
    "fase",
    "provimento",
    "fato_gerador",
    "objeto",
    "tipo_empresa",
    "tipo_entrada",
    "acao",
    "escritorio",
    "classificacao",
    "toi_criado",
    "nota_tecnica",
    "liminar",
]


class Complement(CrawJUD):
    """A class that configures and retrieves an elements bot instance.

    This class interacts with the ELAW system to complete the registration of a process.
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
        """Execute the complement bot.

        This method executes the complement bot by calling the queue method
        for each row in the DataFrame, and handling any exceptions that may
        occur. If the Webdriver is closed unexpectedly, it will be
        reinitialized. The bot will also be stopped if the is_stoped attribute
        is set to True.


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
        """Execute the queue process for complementing registration.

        This method performs a series of operations to complete the registration
        process using the ELAW system. It checks the current search status, formats
        the bot data, and if the process is found, it initializes the registration
        complement by interacting with various web elements. The method logs the
        steps, calculates the execution time, and handles potential exceptions
        during the process.

        Steps:
        1. Check the search status and format bot data.
        2. If the search is successful:
           - Initialize the registration Complement.
           - Locate and click the edit button for complementing processes.
           - Iterate over the bot data to perform specific actions based on keys.
           - Validate fields and participants.
           - Save all changes and confirm the save operation.
           - Log the success message and execution time.
        3. If the search is not successful, raise an error.
        4. Handle any exceptions by raising `ExecutionError`.

        Raises:
            ExecutionError: If the process is not found or an error occurs.

        """
        try:
            search = self.search_bot()
            self.bot_data = self.elawFormats(self.bot_data)

            if search is True:
                self.message = "Inicializando complemento de cadastro"
                self.type_log = "log"
                self.prt()
                edit_proc_button = self.wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.botao_editar_complementar)),
                )
                edit_proc_button.click()

                lista1 = list(self.bot_data.keys())

                start_time = time.perf_counter()

                check_esfera = self.wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.label_esfera)),
                )

                esfera_xls = self.bot_data.get("ESFERA")

                if esfera_xls:
                    if check_esfera.text.lower() != esfera_xls.lower():
                        Complement.esfera(self, esfera_xls)

                for item in lista1:
                    func: Callable[[], None] = getattr(Complement, item.lower(), None)

                    if func and item.lower() != "esfera":
                        func(self)

                end_time = time.perf_counter()
                execution_time = end_time - start_time
                calc = execution_time / 60
                splitcalc = str(calc).split(".")
                minutes = int(splitcalc[0])
                seconds = int(float(f"0.{splitcalc[1]}") * 60)

                self.validar_campos()

                self.validar_advs_participantes()

                self.save_all()

                if self.confirm_save() is True:
                    name_comprovante = self.print_comprovante()
                    self.message = "Processo salvo com sucesso!"

                self.append_success(
                    [self.bot_data.get("NUMERO_PROCESSO"), self.message, name_comprovante],
                    self.message,
                )
                self.message = f"Formulário preenchido em {minutes} minutos e {seconds} segundos"

                self.type_log = "log"
                self.prt()

            elif search is not True:
                raise ExecutionError(message="Processo não encontrado!")

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception_only(e)))
            raise ExecutionError(e=e) from e

    def save_all(self) -> None:
        """Save all changes in the process.

        This method interacts with the web elements to save all changes made
        to the process. It logs the action and clicks the save button.


        """
        self.interact.sleep_load('div[id="j_id_3x"]')
        salvartudo: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_salvar_proc)),
        )
        self.type_log = "log"
        self.message = "Salvando processo novo"
        self.prt()
        salvartudo.click()

    def validar_campos(self) -> None:
        """Validate the required fields.

        This method checks each required field in the process to ensure
        they are properly filled. It logs the validation steps and raises
        an error if any required field is missing.

        Raises:
            ExecutionError: If any required field is missing.

        """
        self.message = "Validando campos"
        self.type_log = "log"
        self.prt()

        validar: dict[str, str] = {"NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO")}
        message_campo: list[str] = []

        for campo in campos_validar:
            try:
                campo_validar: str = self.elements.dict_campos_validar.get(campo)
                command = f"return $('{campo_validar}').text()"
                element = self.driver.execute_script(command)

                if not element or element.lower() == "selecione":
                    raise ExecutionError(message=f'Campo "{campo}" não preenchido')

                message_campo.append(f'<p class="fw-bold">Campo "{campo}" Validado | Texto: {element}</p>')
                validar.update({campo.upper(): element})

            except Exception as e:
                self.logger.exception("".join(traceback.format_exception_only(e)))
                try:
                    message = e.message

                except Exception:
                    message = str(e)

                validar.update({campo.upper(): message})

                self.message = message
                self.type_log = "info"
                self.prt()

        self.append_validarcampos([validar])
        message_campo.append('<p class="fw-bold">Campos validados!</p>')
        self.message = "".join(message_campo)
        self.type_log = "info"
        self.prt()

    def validar_advogado(self) -> str:
        """Validate the responsible lawyer.

        This method ensures that the responsible lawyer field is filled and
        properly selected. It logs the validation steps and raises an error
        if the field is not properly filled.

        Returns:
        str
            The name of the responsible lawyer.


        Raises:
            ExecutionError: If the responsible lawyer field is not filled.

        """
        self.message = "Validando advogado responsável"
        self.type_log = "log"
        self.prt()

        campo_validar = self.elements.dict_campos_validar.get("advogado_interno")
        command = f"return $('{campo_validar}').text()"
        element = self.driver.execute_script(command)

        if not element or element.lower() == "selecione":
            raise ExecutionError(message='Campo "Advogado Responsável" não preenchido')

        self.message = f'Campo "Advogado Responsável" | Texto: {element}'
        self.type_log = "info"
        self.prt()

        sleep(0.5)

        return element

    def validar_advs_participantes(self) -> None:
        """Validate participating lawyers.

        This method ensures that the responsible lawyer is present in the
        list of participating lawyers. It logs the validation steps and
        raises an error if the responsible lawyer is not found.

        Raises:
            ExecutionError: If the responsible lawyer is not found in the list of participating lawyers.

        """
        data_bot = self.bot_data
        adv_name = data_bot.get("ADVOGADO_INTERNO", self.validar_advogado())

        if not adv_name.strip():
            raise ExecutionError(message="Necessário advogado interno para validação!")

        self.message = "Validando advogados participantes"
        self.type_log = "log"
        self.prt()

        tb_Advs = self.driver.find_element(By.CSS_SELECTOR, self.elements.tb_advs_resp)  # noqa: N806

        not_adv = None
        with suppress(NoSuchElementException):
            tr_not_adv = self.elements.tr_not_adv
            not_adv = tb_Advs.find_element(By.CSS_SELECTOR, tr_not_adv)

        if not_adv is not None:
            raise ExecutionError(message="Sem advogados participantes!")

        advs = tb_Advs.find_elements(By.TAG_NAME, "tr")

        for adv in advs:
            advogado = adv.find_element(By.TAG_NAME, "td").text
            if advogado.lower() == adv_name.lower():
                break

        else:
            raise ExecutionError(message="Advogado responsável não encontrado na lista de advogados participantes!")

        self.message = "Advogados participantes validados"
        self.type_log = "info"
        self.prt()

    def confirm_save(self) -> bool:
        """Confirm the save operation.

        This method checks if the process was successfully saved by verifying
        the URL or checking for error messages. It logs the outcome and raises
        an error if the save was not successful.

        Returns:
            bool: True if the save was successful, False otherwise.


        Raises:
            ExecutionError: If the process was not saved successfully

        """
        wait_confirm_save = None

        with suppress(TimeoutException):
            wait_confirm_save: WebElement = WebDriverWait(self.driver, 20).until(
                ec.url_to_be("https://amazonas.elaw.com.br/processoView.elaw"),
            )

        if wait_confirm_save:
            return True

        if not wait_confirm_save:
            ErroElaw: WebElement | str = None  # noqa: N806
            with suppress(TimeoutException, NoSuchElementException):
                ErroElaw = (  # noqa: N806
                    self.wait.until(
                        ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.div_messageerro_css)),
                        message="Erro ao encontrar elemento",
                    )
                    .find_element(By.TAG_NAME, "ul")
                    .text
                )

            if not ErroElaw:
                ErroElaw = "Cadastro do processo nao finalizado, verificar manualmente"  # noqa: N806

            raise ExecutionError(ErroElaw)

    def print_comprovante(self) -> str:
        """Print the comprovante (receipt) of the registration.

        This method captures a screenshot of the process and saves it
        as a comprovante file.

        Returns
        -------
        str
            The name of the comprovante file.

        """
        name_comprovante = f"Comprovante Cadastro - {self.bot_data.get('NUMERO_PROCESSO')} - PID {self.pid}.png"
        savecomprovante = Path(self.output_dir_path).resolve().joinpath(name_comprovante)
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante

    @classmethod
    def advogado_interno(cls, self: Self) -> None:
        """Inform the internal lawyer.

        This method inputs the internal lawyer information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.

        Raises
        ------
            ExecutionError: If the internal lawyer is not found.

        """
        self.message = "informando advogado interno"
        self.type_log = "log"
        self.prt()

        input_adv_responsavel: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_adv_responsavel)),
        )
        input_adv_responsavel.click()
        self.interact.send_key(input_adv_responsavel, self.bot_data.get("ADVOGADO_INTERNO"))

        css_wait_adv = r"#j_id_3k_1\:autoCompleteLawyer_panel > ul > li"

        wait_adv = None

        with suppress(TimeoutException):
            wait_adv: WebElement = WebDriverWait(self.driver, 25).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, css_wait_adv)),
            )

        if wait_adv:
            wait_adv.click()
        elif not wait_adv:
            raise ExecutionError(message="Advogado interno não encontrado")

        self.interact.sleep_load('div[id="j_id_3x"]')

        div_select_Adv: WebElement = self.wait.until(  # noqa: N806
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_div_select_Adv)),
        )
        div_select_Adv.click()

        self.interact.sleep_load('div[id="j_id_3x"]')

        input_select_adv: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_input_select_Adv)),
        )
        input_select_adv.click()

        self.interact.send_key(input_select_adv, self.bot_data.get("ADVOGADO_INTERNO"))
        input_select_adv.send_keys(Keys.ENTER)

        self.driver.execute_script(f"document.querySelector('{self.elements.css_div_select_Adv}').blur()")

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Advogado interno informado!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def esfera(cls, self: Self, text: str = "Judicial") -> None:
        """Handle the selection of the judicial sphere in the process.

        This function performs the following steps:
        1. Selects the judicial sphere element.
        2. Sets the text to "Judicial".
        3. Logs the message "Informando esfera do processo".
        4. Calls the select2_elaw method to select the element.
        5. Waits for the loading of the specified div element.
        6. Logs the message "Esfera Informada!".

        Parameters
        ----------
        self : Self
            The instance of the class.
        text : str, optional
            The text to set for the judicial sphere, by default "Judicial".

        """
        element_select = self.elements.css_esfera_judge
        self.message = "Informando esfera do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Esfera Informada!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def estado(cls, self: Self) -> None:
        """Update the state of the process in the system.

        This method retrieves the state information from `self.bot_data` using the key "ESTADO",
        logs the action, and updates the state input field in the system using the `select2_elaw` method.
        It then waits for the system to load the changes.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        key = "ESTADO"
        element_select = self.elements.estado_input
        text = str(self.bot_data.get(key, None))

        self.message = "Informando estado do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Estado do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def comarca(cls, self: Self) -> None:
        """Inform the "comarca" (jurisdiction) of the process.

        This method retrieves the comarca information from the bot data,
        selects the appropriate input element, and interacts with the
        interface to input the comarca information.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        text = str(self.bot_data.get("COMARCA"))
        element_select = self.elements.comarca_input

        self.message = "Informando comarca do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Comarca do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def foro(cls, self: Self) -> None:
        """Update the forum (foro) information for the process.

        This method selects the appropriate forum input element and updates it with the
        forum information retrieved from `self.bot_data`. It logs the actions performed
        and interacts with the necessary elements on the page to ensure the forum information
        is correctly updated.

        Parameters
        ----------
        self : Self
            The instance of the class.

        """
        element_select = self.elements.foro_input
        text = str(self.bot_data.get("FORO"))

        self.message = "Informando foro do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Foro do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def vara(cls, self: Self) -> None:
        """Update the "vara" (court) information for the process.

        This method retrieves the "VARA" data from the bot's data, selects the appropriate
        input element for "vara", and interacts with the ELAW system to update the information.
        It logs messages before and after the interaction to indicate the status of the operation.

        Parameters
        ----------
        self : Self
            The instance of the class.

        """
        text = self.bot_data.get("VARA")
        element_select = self.elements.vara_input

        self.message = "Informando vara do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Vara do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def unidade_consumidora(cls, self: Self) -> None:
        """Handle the process of informing the consumer unit in the web application.

        This function performs the following steps:
        1. Logs the start of the process.
        2. Waits for the input field for the consumer unit to be present in the DOM.
        3. Clicks on the input field.
        4. Clears any existing text in the input field.
        5. Sends the consumer unit data to the input field.
        6. Logs the completion of the process.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando unidade consumidora"
        self.type_log = "log"
        self.prt()

        input_uc: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_input_uc)),
        )
        input_uc.click()

        self.interact.clear(input_uc)

        self.interact.send_key(input_uc, self.bot_data.get("UNIDADE_CONSUMIDORA"))

        self.message = "Unidade consumidora informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def localidade(cls, self: Self) -> None:
        """Inform the locality of the process.

        This method inputs the locality information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando localidade"
        self.type_log = "log"
        self.prt()

        css_input_bairro = (
            'input[id="j_id_3k_1:j_id_3k_4_2_2_7_9_44_2:j_id_3k_4_2_2_7_9_44_3_1_2_2_1_1:fieldid_13351fieldText"]'
        )

        bairro_ = self.bot_data.get("LOCALIDADE")

        input_bairro = self.driver.find_element(By.CSS_SELECTOR, css_input_bairro)
        input_bairro.click()
        self.interact.clear(input_bairro)
        self.interact.send_key(input_bairro, bairro_)

        self.driver.execute_script(f"document.querySelector('{self.elements.css_valor_causa}').blur()")

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Localidade informada!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def bairro(cls, self: Self) -> None:
        """Inform the neighborhood of the process.

        This method inputs the neighborhood information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando bairro"
        self.type_log = "log"
        self.prt()

        css_input_bairro = (
            'input[id="j_id_3k_1:j_id_3k_4_2_2_8_9_44_2:j_id_3k_4_2_2_8_9_44_3_1_2_2_1_1:fieldid_9237fieldText"]'
        )

        bairro_ = self.bot_data.get("BAIRRO")

        input_bairro = self.driver.find_element(By.CSS_SELECTOR, css_input_bairro)
        input_bairro.click()
        self.interact.clear(input_bairro)
        self.interact.send_key(input_bairro, bairro_)

        self.driver.execute_script(f"document.querySelector('{self.elements.css_valor_causa}').blur()")

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Bairro informado!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def divisao(cls, self: Self) -> None:
        """Inform the division of the process.

        This method inputs the division information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando divisão"
        self.type_log = "log"
        self.prt()

        sleep(0.5)
        text = str(self.bot_data.get("DIVISAO"))

        self.select2_elaw(self.elements.element_select, text)

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Divisão informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def data_citacao(cls, self: Self) -> None:
        """Inform the citation date in the process.

        This method inputs the citation date into the system and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando data de citação"
        self.type_log = "log"
        self.prt()

        data_citacao: WebElement = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.css_data_citacao)),
        )
        self.interact.clear(data_citacao)
        self.interact.sleep_load('div[id="j_id_3x"]')
        self.interact.send_key(data_citacao, self.bot_data.get("DATA_CITACAO"))
        sleep(2)
        self.driver.execute_script(f"document.querySelector('{self.elements.css_data_citacao}').blur()")
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Data de citação informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def fase(cls, self: Self) -> None:
        """Inform the phase of the process.

        This method inputs the phase information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        element_select = self.elements.fase_input
        text = self.bot_data.get("FASE")

        self.message = "Informando fase do processo"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Fase informada!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def provimento(cls, self: Self) -> None:
        """Inform the anticipatory provision in the process.

        This method inputs the anticipatory provision information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        text = self.bot_data.get("PROVIMENTO")
        element_select = self.elements.provimento_input

        self.message = "Informando provimento antecipatório"
        self.type_log = "log"
        self.prt()

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Provimento antecipatório informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def valor_causa(cls, self: Self) -> None:
        """Inform the value of the cause.

        This method inputs the value of the cause into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando valor da causa"
        self.type_log = "log"
        self.prt()

        valor_causa: WebElement = self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, self.elements.css_valor_causa)),
            message="Erro ao encontrar elemento",
        )

        valor_causa.click()
        sleep(0.5)
        valor_causa.clear()

        self.interact.send_key(valor_causa, self.bot_data.get("VALOR_CAUSA"))
        self.driver.execute_script(f"document.querySelector('{self.elements.css_valor_causa}').blur()")

        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Valor da causa informado!"
        self.type_log = "info"
        self.prt()

    @classmethod
    def fato_gerador(cls, self: Self) -> None:
        """Inform the triggering event (fato gerador).

        This method inputs the triggering event information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando fato gerador"
        self.type_log = "log"
        self.prt()

        element_select = self.elements.fato_gerador_input
        text = self.bot_data.get("FATO_GERADOR")

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Fato gerador informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def desc_objeto(cls, self: Self) -> None:
        """Fill in the description object field.

        This method inputs the description of the object into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        input_descobjeto = self.wait.until(
            ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.input_descobjeto_css)),
        )
        self.interact.click(input_descobjeto)

        text = self.bot_data.get("DESC_OBJETO")

        self.interact.clear(input_descobjeto)
        self.interact.send_key(input_descobjeto, text)
        self.driver.execute_script(f"document.querySelector('{self.elements.input_descobjeto_css}').blur()")
        self.interact.sleep_load('div[id="j_id_3x"]')

    @classmethod
    def objeto(cls, self: Self) -> None:
        """Inform the object of the process.

        This method inputs the object information into the system
        and ensures it is properly selected.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando objeto do processo"
        self.type_log = "log"
        self.prt()

        element_select = self.elements.objeto_input
        text = self.bot_data.get("OBJETO")

        self.select2_elaw(element_select, text)
        self.interact.sleep_load('div[id="j_id_3x"]')

        self.message = "Objeto do processo informado!"
        self.type_log = "log"
        self.prt()

    @classmethod
    def tipo_empresa(cls, self: Self) -> None:
        """Set the type of company and update relevant UI elements.

        This method determines the type of company (either "Ativa" or "Passiva") based on the
        "TIPO_EMPRESA" value in `self.bot_data`. It then updates the UI elements for
        contingencia and tipo_polo with the appropriate values and logs the actions performed.

        Parameters
        ----------
        self : Self
            The instance of the class.


        """
        self.message = "Informando contingenciamento"
        self.type_log = "log"
        self.prt()

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

        self.message = "Contingenciamento informado!"
        self.type_log = "info"
        self.prt()
