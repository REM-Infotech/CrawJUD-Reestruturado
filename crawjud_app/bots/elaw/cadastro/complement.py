"""Module for managing registration completion tasks in the ELAW system.

This module handles the completion and supplementation of registration data within the ELAW
system. It automates the process of filling in missing or additional registration details.

Classes:
    Complement: Manages registration completion by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)
    campos_validar (list): Fields to validate during registration completion

"""

import traceback
from contextlib import suppress
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

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
ELEMENT_LOAD = 'div[id="j_id_48"]'


class CadastroComplementar(ClassBot):
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
            ExecutionError: If the responsible lawyer
                is not found in the list of participating lawyers.

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
                message=(
                    "Advogado responsável não encontrado",
                    " na lista de advogados participantes!",
                ),
            )

        self.message = "Advogados participantes validados"
        self.type_log = "info"
        self.prt()

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
        self.interact.sleep_load(ELEMENT_LOAD)

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

        self.interact.sleep_load(ELEMENT_LOAD)

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

        self.interact.sleep_load(ELEMENT_LOAD)

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

        self.interact.sleep_load(ELEMENT_LOAD)

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
        self.interact.sleep_load(ELEMENT_LOAD)
        self.interact.send_key(data_citacao, self.bot_data.get("DATA_CITACAO"))
        sleep(2)
        id_element = data_citacao.get_attribute("id")
        id_input_css = f'[id="{id_element}"]'
        comando = f"document.querySelector('{id_input_css}').blur()"
        self.driver.execute_script(comando)
        self.interact.sleep_load(ELEMENT_LOAD)

        self.message = "Data de citação informada!"
        self.type_log = "log"
        self.prt()
