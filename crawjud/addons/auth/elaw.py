"""Módulo de controle de autenticação Elaw."""

from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec

from crawjud.addons.auth.controller import AuthController


class ElawAuth(AuthController):
    """Classe de autenticação Elaw."""

    def auth(self) -> bool:
        """Authenticate on the eLAW platform using provided credentials.

        Returns:
            bool: True if authentication is successful; False otherwise.

        Navigates to the login page, enters credentials, and verifies the URL after login.

        """
        try:
            self.driver.get("https://amazonas.elaw.com.br/login")

            # wait until page load
            username: WebElement = self.wait.until(ec.presence_of_element_located((By.ID, "username")))
            username.send_keys(self.username)

            password: WebElement = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#password")))
            password.send_keys(self.password)

            entrar: WebElement = self.wait.until(ec.presence_of_element_located((By.ID, "j_id_a_1_5_f")))
            entrar.click()

            sleep(7)

            url = self.driver.current_url
            return url != "https://amazonas.elaw.com.br/login"

        except Exception as e:
            raise e
