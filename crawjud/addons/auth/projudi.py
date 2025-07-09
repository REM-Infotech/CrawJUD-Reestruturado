"""Módulo de controle de autenticação Projudi."""

from contextlib import suppress
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from crawjud.addons.auth.controller import AuthController
from crawjud.exceptions.bot import LoginSystemError


class ProjudiAuth(AuthController):
    """Classe de autenticação PROJUDI."""

    def auth(self) -> bool:
        """Authenticate on PROJUDI platform using username and password.

        Returns:
            bool: True if the login process completes successfully; False otherwise.

        """
        try:
            self.driver.get(self.elements.url_login)

            sleep(1.5)

            self.driver.refresh()

            username: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.campo_username,
                )),
            )
            username.send_keys(self.username)

            password = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.campo_passwd
            )
            password.send_keys(self.password)

            entrar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.btn_entrar
            )
            entrar.click()

            check_login = None

            with suppress(TimeoutException):
                check_login = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.chk_login,
                    )),
                )

            alert = None
            with suppress(TimeoutException):
                alert: type[Alert] = WebDriverWait(self.driver, 5).until(
                    ec.alert_is_present()
                )

            if alert:
                alert.accept()

            return check_login is not None

        except Exception as e:
            raise LoginSystemError(exception=e) from e
