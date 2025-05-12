"""Authentication module: Authenticate users across systems; perform login and certificate tasks promptly.

This module provides the AuthBot class with methods for authentication on ESAJ, PROJUDI, eLAW,
and PJE systems. Each method follows error handling and logging conventions.
"""

import logging
import os
import platform
import string
import subprocess  # nosec: B404
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import Callable

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

from crawjud.bot.core import CrawJUD

if platform.system() == "Windows":
    from crawjud.bot.core import Application

logger = logging.getLogger(__name__)


class AuthBot(CrawJUD):
    """Handle user authentication across multiple legal system platforms.

    This class implements methods for different systems to perform login and certificate acceptance.
    """

    def __init__(self) -> None:
        """Initialize AuthBot instance.

        Setup any preliminary attributes required for subsequent authentication.
        """
        # Initialize any additional attributes here

    def auth(self) -> bool:
        """Dynamically execute the proper authentication method based on the system.

        Returns:
            bool: The result from the invoked authentication method.

        Raises:
            RuntimeError: When a system-specific auth method cannot be found.

        """
        to_call: Callable[[], bool] = getattr(AuthBot, f"{self.system.lower()}_auth", None)
        if to_call:
            return to_call(self)

        raise RuntimeError("Sistema Não encontrado!")

    def projudi_auth(self) -> bool:
        """Authenticate on PROJUDI platform using username and password.

        Returns:
            bool: True if the login process completes successfully; False otherwise.

        """
        try:
            self.driver.get(self.elements.url_login)

            sleep(1.5)

            self.driver.refresh()

            username: WebElement = self.wait.until(
                ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.campo_username)),
            )
            username.send_keys(self.username)

            password = self.driver.find_element(By.CSS_SELECTOR, self.elements.campo_passwd)
            password.send_keys(self.password)

            entrar = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_entrar)
            entrar.click()

            check_login = None

            with suppress(TimeoutException):
                check_login = WebDriverWait(self.driver, 10).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.chk_login)),
                )

            alert = None
            with suppress(TimeoutException):
                alert: type[Alert] = WebDriverWait(self.driver, 5).until(ec.alert_is_present())

            if alert:
                alert.accept()

            return check_login is not None

        except Exception as e:
            raise e

    def elaw_auth(self) -> bool:
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

    def pje_auth(self) -> bool:
        """Authenticate on the PJE system by providing username and password.

        Returns:
            bool: True if login was successful; False otherwise.

        Fills all required fields and checks the status by verifying the page URL.

        """
        try:
            self.driver.get(self.elements.url_login)

            login = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.login_input)))
            password = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.password_input)))
            entrar = self.wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.btn_entrar)))

            login.send_keys(self.username)
            sleep(0.5)
            password.send_keys(self.password)
            sleep(0.5)
            entrar.click()

            logado = None
            with suppress(TimeoutException):
                logado = WebDriverWait(self.driver, 10).until(ec.url_to_be(self.elements.chk_login))

            return logado is not None

        except Exception as e:
            raise e

    def accept_cert(self, accepted_dir: str) -> None:
        """Automatically accept a certificate using the certificate management tool.

        Args:
            accepted_dir (str): Directory path where accepted certificates are recorded.

        Executes certificate acceptance and copies necessary files.

        """
        try:
            path = r"C:\Users\%USERNAME%\AppData\Local\Softplan Sistemas\Web Signer"
            resolved_path = os.path.expandvars(path)

            app = Application(backend="uia").connect(path=resolved_path, cache_enable=True)
            janela_principal = app.window()
            janela_principal.set_focus()
            button = janela_principal.descendants(control_type="Button")
            checkbox = janela_principal.descendants(control_type="CheckBox")

            sleep(0.5)

            checkbox[0].click_input()
            sleep(0.5)
            button[1].click_input()

            target_directory = Path(accepted_dir).parent.joinpath("chrome").resolve()

            target_directory.mkdir(exist_ok=True)
            source_directory = self.chr_dir

            try:
                comando = ["xcopy", source_directory, target_directory, "/E", "/H", "/C", "/I"]
                resultados = subprocess.run(  # nosec: B603
                    comando,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                logger.info(str(resultados.stdout))

            except Exception as e:
                raise e

            with open(Path(accepted_dir), "w", encoding="utf-8") as f:  # noqa: FURB103
                f.write("")

        except Exception as e:
            raise e
