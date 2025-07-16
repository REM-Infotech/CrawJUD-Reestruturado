"""Módulo de controle de autenticação Pje."""

from contextlib import suppress
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from crawjud.addons.auth import AuthController


class PjeAuth(AuthController, name="pje"):
    """Classe de autenticação PJE."""

    def auth(self) -> bool:
        """Authenticate on the PJE system by providing username and password.

        Returns:
            bool: True if login was successful; False otherwise.

        Fills all required fields and checks the status by verifying the page URL.

        """
        try:
            self.driver.get(self.elements.url_login)

            login = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.login_input,
                ))
            )
            password = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.password_input,
                ))
            )
            entrar = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.btn_entrar,
                ))
            )

            login.send_keys(self.username)
            sleep(0.5)
            password.send_keys(self.password)
            sleep(0.5)
            entrar.click()

            logado = None
            with suppress(TimeoutException):
                logado = WebDriverWait(self.driver, 10).until(
                    ec.url_to_be(self.elements.chk_login)
                )

            return logado is not None

        except Exception as e:
            raise e
