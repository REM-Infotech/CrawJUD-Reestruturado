from __future__ import annotations

import os
import string
from contextlib import suppress
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

from crawjud.addons.auth.controller import AuthController

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class EsajAuth(AuthController):
    def esaj_auth(self) -> bool:
        """Authenticate on ESAJ system using certificate or credentials.

        Returns:
            bool: True if authentication is successful; False otherwise.

        Waits for page elements, selects certificate if needed, and verifies login.

        """
        try:
            loginuser = "".join(filter(lambda x: x not in string.punctuation, self.username))
            passuser = self.password
            if self.login_method == "cert":
                self.driver.get(self.elements.url_login_cert)
                sleep(3)
                loginopt: WebElement = self.wait.until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, 'select[id="certificados"]')),
                )
                loginopt = loginopt.find_elements(By.TAG_NAME, "option")

                item = None

                try:
                    item = next(filter(lambda item: loginuser in item.text, loginopt), None)

                except Exception as e:
                    raise e
                if item:
                    try:
                        sencert = item.get_attribute("value")
                        select = Select(self.driver.find_element(By.CSS_SELECTOR, 'select[id="certificados"]'))
                        select.select_by_value(sencert)
                        entrar = self.driver.find_element(By.XPATH, '//*[@id="submitCertificado"]')
                        entrar.click()
                        sleep(2)

                        user_accept_cert_dir = os.path.join(self.path_accepted, "ACCEPTED")
                        if not os.path.exists(user_accept_cert_dir):
                            self.accept_cert(user_accept_cert_dir)

                    except Exception as e:
                        raise e

                elif not item:
                    return False

                checkloged = None
                with suppress(TimeoutException):
                    checkloged = WebDriverWait(self.driver, 15).until(
                        ec.presence_of_element_located(
                            (
                                By.CSS_SELECTOR,
                                "#esajConteudoHome > table:nth-child(4) > tbody > tr > td.esajCelulaDescricaoServicos",
                            ),
                        ),
                    )

                if not checkloged:
                    return False

                return True

            self.driver.get(self.elements.url_login)
            sleep(3)

            userlogin = self.driver.find_element(By.CSS_SELECTOR, self.elements.campo_username)
            userlogin.click()
            userlogin.send_keys(loginuser)

            userpass = self.driver.find_element(By.CSS_SELECTOR, self.elements.campo_passwd)
            userpass.click()
            userpass.send_keys(passuser)
            entrar = self.driver.find_element(By.CSS_SELECTOR, self.elements.btn_entrar)
            entrar.click()
            sleep(2)

            checkloged = None
            with suppress(TimeoutException):
                checkloged = WebDriverWait(self.driver, 15).until(
                    ec.presence_of_element_located((By.CSS_SELECTOR, self.elements.chk_login)),
                )

            return checkloged is not None

        except Exception as e:
            raise e
