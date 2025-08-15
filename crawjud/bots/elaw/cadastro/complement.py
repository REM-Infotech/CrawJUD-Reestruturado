"""Module for managing registration completion tasks in the ELAW system.

This module handles the completion and supplementation of registration data within the ELAW
system. It automates the process of filling in missing or additional registration details.

Classes:
    Complement: Manages registration completion by extending the CrawJUD base class

Attributes:
    type_doc (dict): Maps document lengths to document types (CPF/CNPJ)
    campos_validar (list): Fields to validate during registration completion

"""

from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from crawjud.interfaces.controllers.bots.systems.elaw import ElawBot

type_doc = {11: "cpf", 14: "cnpj"}


ELEMENT_LOAD = 'div[id="j_id_48"]'


class CadastroComplementar(ElawBot):
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

        input_uc = self.wait.until(
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

        data_citacao = self.wait.until(
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
