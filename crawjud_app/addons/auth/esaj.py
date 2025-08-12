"""Módulo de controle de autenticação Esaj."""

from __future__ import annotations

import string
from contextlib import suppress
from pathlib import Path
from time import sleep
from typing import TYPE_CHECKING

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

from crawjud_app.addons.auth import AuthController

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class EsajAuth(AuthController):
    """Classe de autenticação Esaj."""

    def auth(self) -> bool:  # noqa: D102
        loginuser = "".join(
            filter(lambda x: x not in string.punctuation, self.username),
        )
        passuser = self.password
        if self.login_method == "cert":
            self.driver.get(self.elements.url_login_cert)
            sleep(3)
            loginopt: WebElement = self.wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'select[id="certificados"]',
                )),
            )
            loginopt = loginopt.find_elements(By.TAG_NAME, "option")

            item = None

            item = next(
                filter(lambda item: loginuser in item.text, loginopt),
                None,
            )
            if item:
                sencert = item.get_attribute("value")
                select = Select(
                    self.driver.find_element(
                        By.CSS_SELECTOR,
                        'select[id="certificados"]',
                    ),
                )
                select.select_by_value(sencert)
                entrar = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="submitCertificado"]',
                )
                entrar.click()
                sleep(2)

                user_accept_cert_dir = Path(self.path_accepted) / "ACCEPTED"
                if not user_accept_cert_dir.exists():
                    self.accept_cert(user_accept_cert_dir)

            elif not item:
                return False

            checkloged = None
            with suppress(TimeoutException):
                checkloged = WebDriverWait(self.driver, 15).until(
                    ec.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            (
                                "#esajConteudoHome > table:nth-child(4)",
                                " > tbody > ",
                                "tr > td.esajCelulaDescricaoServicos",
                            ),
                        ),
                    ),
                )

            return checkloged is not None

        self.driver.get(self.elements.url_login)
        sleep(3)

        userlogin = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.campo_username,
        )
        userlogin.click()
        userlogin.send_keys(loginuser)

        userpass = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.campo_2_login,
        )
        userpass.click()
        userpass.send_keys(passuser)
        entrar = self.driver.find_element(
            By.CSS_SELECTOR,
            self.elements.btn_entrar,
        )
        entrar.click()
        sleep(2)

        checkloged = None

        try:
            checkloged = WebDriverWait(self.driver, 15).until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    self.elements.chk_login,
                )),
            )
        except TimeoutException:
            return False

        else:
            return checkloged is not None
