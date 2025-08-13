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
from collections.abc import Callable
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Self

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud_app.abstract.bot import ClassBot
from crawjud_app.common.exceptions.bot import ExecutionError

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
    "escritorio_externo",
    "classificacao",
    "toi_criado",
    "nota_tecnica",
    "liminar",
]


class CadastroComplementar(ClassBot):
    """A class that configures and retrieves an elements bot instance.

    This class interacts with the ELAW system to complete the registration of a process.
    """

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
        """Initialize the complement class.

        This method initializes the complement class by calling the base class's
        __init__ method and setting up the bot and authentication.

        Parameters
        ----------
        *args : tuple
            A tuple of arguments to be passed to the base class's __init__ method.
        **kwargs : dict
            A dictionary of keyword arguments to be passed to the base class's
            __init__ method.


        """
        super().__init__()
        self.module_bot = __name__

        super().setup(*args, **kwargs)
        super().auth_bot()
        self.start_time = time.perf_counter()

    def execution(self) -> None:
        """Execute the complement bot.

        This method executes the complement bot by calling the queue method
        for each row in the DataFrame, and handling any exceptions that may
        occur. If the Webdriver is closed unexpectedly, it will be
        reinitialized. The bot will also be stopped if the isStoped attribute
        is set to True.


        """
        frame = [self.elaw_formats(item) for item in self.dataFrame()]
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

            if search is True:
                start_time = time.perf_counter()
                self.message = "Inicializando complemento de cadastro"
                self.type_log = "log"
                self.prt()

                lista1 = list(self.bot_data.keys())
                check_esfera = self.wait.until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.label_esfera,
                    )),
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
                    [
                        self.bot_data.get("NUMERO_PROCESSO"),
                        self.message,
                        name_comprovante,
                    ],
                    self.message,
                )
                self.message = (
                    f"Formulário preenchido em {minutes} minutos e {seconds} segundos"
                )

                self.type_log = "log"
                self.prt()

            elif search is not True:
                raise ExecutionError(message="Processo não encontrado!")

        except Exception as e:
            self.logger.exception("".join(traceback.format_exception(e)))
            raise ExecutionError(e=e) from e

    def save_all(self) -> None:
        """Save all changes in the process.

        This method interacts with the web elements to save all changes made
        to the process. It logs the action and clicks the save button.


        """
        self.interact.sleep_load('div[id="j_id_48"]')
        salvartudo: WebElement = self.wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                self.elements.css_salvar_proc,
            )),
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

        validar: dict[str, str] = {
            "NUMERO_PROCESSO": self.bot_data.get("NUMERO_PROCESSO"),
        }
        message_campo: list[str] = []

        for campo in campos_validar:
            try:
                campo_validar: str = self.elements.dict_campos_validar.get(campo)
                command = f"return $('{campo_validar}').text()"
                element = self.driver.execute_script(command)

                if not element or element.lower() == "selecione":
                    raise ExecutionError(message=f'Campo "{campo}" não preenchido')

                message_campo.append(
                    f'<p class="fw-bold">Campo "{campo}" Validado | Texto: {element}</p>',
                )
                validar.update({campo.upper(): element})

            except Exception as e:
                self.logger.exception("".join(traceback.format_exception(e)))
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
            raise ExecutionError(
                message='Campo "Advogado Responsável" não preenchido',
            )

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
            raise ExecutionError(
                message="Necessário advogado interno para validação!",
            )

        self.message = "Validando advogados participantes"
        self.type_log = "log"
        self.prt()

        tabela_advogados = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.tabela_advogados_resp,
        )

        not_adv = None
        with suppress(NoSuchElementException):
            tr_not_adv = self.elements.tr_not_adv
            not_adv = tabela_advogados.find_element(By.CSS_SELECTOR, tr_not_adv)

        if not_adv is not None:
            raise ExecutionError(message="Sem advogados participantes!")

        advs = tabela_advogados.find_elements(By.TAG_NAME, "tr")

        for adv in advs:
            advogado = adv.find_element(By.TAG_NAME, "td").text
            if advogado.lower() == adv_name.lower():
                break

        else:
            raise ExecutionError(
                message="Advogado responsável não encontrado na lista de advogados participantes!",
            )

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
            erro_elaw: str | None = None
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

            raise ExecutionError(erro_elaw)

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
        savecomprovante = (
            Path(self.output_dir_path).resolve().joinpath(name_comprovante)
        )
        self.driver.get_screenshot_as_file(savecomprovante)
        return name_comprovante

    def esfera(self, text: str = "Judicial") -> None:
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

        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )
        self.interact.sleep_load('div[id="j_id_48"]')

        self.message = "Esfera Informada!"
        self.type_log = "info"
        self.prt()

    def unidade_consumidora(self) -> None:
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
            ec.presence_of_element_located((By.XPATH, self.elements.css_input_uc)),
        )
        input_uc.click()

        self.interact.clear(input_uc)

        self.interact.send_key(input_uc, self.bot_data.get("UNIDADE_CONSUMIDORA"))

        self.message = "Unidade consumidora informada!"
        self.type_log = "log"
        self.prt()

    def localidade(self) -> None:
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

        localidade = self.bot_data.get("LOCALIDADE")

        input_localidade = self.driver.find_element(
            By.XPATH,
            self.elements.localidade,
        )
        input_localidade.click()
        self.interact.clear(input_localidade)
        self.interact.send_key(input_localidade, localidade)

        id_element = input_localidade.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.interact.sleep_load('div[id="j_id_48"]')

        self.message = "Localidade informada!"
        self.type_log = "info"
        self.prt()

    def bairro(self) -> None:
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

        bairro_ = self.bot_data.get("BAIRRO")

        input_bairro = self.driver.find_element(By.XPATH, self.elements.bairro_input)
        input_bairro.click()
        self.interact.clear(input_bairro)
        self.interact.send_key(input_bairro, bairro_)

        id_element = input_bairro.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)

        self.interact.sleep_load('div[id="j_id_48"]')

        self.message = "Bairro informado!"
        self.type_log = "info"
        self.prt()

    def divisao(self) -> None:
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
        element_select = self.elements.divisao_select
        self.select2_elaw(
            self.wait.until(
                ec.presence_of_element_located((By.XPATH, element_select)),
            ),
            text,
        )

        self.interact.sleep_load('div[id="j_id_48"]')

        self.message = "Divisão informada!"
        self.type_log = "log"
        self.prt()

    def data_citacao(self) -> None:
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
            ec.presence_of_element_located((By.XPATH, self.elements.data_citacao)),
        )
        self.interact.clear(data_citacao)
        self.interact.sleep_load('div[id="j_id_48"]')
        self.interact.send_key(data_citacao, self.bot_data.get("DATA_CITACAO"))
        sleep(2)
        id_element = data_citacao.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)
        self.interact.sleep_load('div[id="j_id_48"]')

        self.message = "Data de citação informada!"
        self.type_log = "log"
        self.prt()
