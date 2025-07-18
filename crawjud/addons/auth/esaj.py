"""Módulo de controle de autenticação Esaj."""

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

from crawjud.addons.auth import AuthController

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class EsajAuth(AuthController):
    """Classe de autenticação Esaj."""

    def auth(self) -> bool:  # noqa: D102
        try:
            loginuser = "".join(
                filter(lambda x: x not in string.punctuation, self.username)
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

                try:
                    item = next(
                        filter(lambda item: loginuser in item.text, loginopt), None
                    )

                except Exception as e:
                    raise e
                if item:
                    try:
                        sencert = item.get_attribute("value")
                        select = Select(
                            self.driver.find_element(
                                By.CSS_SELECTOR, 'select[id="certificados"]'
                            )
                        )
                        select.select_by_value(sencert)
                        entrar = self.driver.find_element(
                            By.XPATH, '//*[@id="submitCertificado"]'
                        )
                        entrar.click()
                        sleep(2)

                        user_accept_cert_dir = os.path.join(
                            self.path_accepted, "ACCEPTED"
                        )
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

            userlogin = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.campo_username
            )
            userlogin.click()
            userlogin.send_keys(loginuser)

            userpass = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.campo_passwd
            )
            userpass.click()
            userpass.send_keys(passuser)
            entrar = self.driver.find_element(
                By.CSS_SELECTOR, self.elements.btn_entrar
            )
            entrar.click()
            sleep(2)

            checkloged = None
            with suppress(TimeoutException):
                checkloged = WebDriverWait(self.driver, 15).until(
                    ec.presence_of_element_located((
                        By.CSS_SELECTOR,
                        self.elements.chk_login,
                    )),
                )

            return checkloged is not None

        except Exception as e:
            raise e

    # def accept_cert(self, accepted_dir: str) -> None:
    #     """Automatically accept a certificate using the certificate management tool.

    #     Args:
    #         accepted_dir (str): Directory path where accepted certificates are recorded.

    #     Executes certificate acceptance and copies necessary files.

    #     """
    #     try:
    #         path = r"C:\Users\%USERNAME%\AppData\Local\Softplan Sistemas\Web Signer"
    #         resolved_path = os.path.expandvars(path)

    #         app = Application(backend="uia").connect(path=resolved_path, cache_enable=True)
    #         janela_principal = app.window()
    #         janela_principal.set_focus()
    #         button = janela_principal.descendants(control_type="Button")
    #         checkbox = janela_principal.descendants(control_type="CheckBox")

    #         sleep(0.5)

    #         checkbox[0].click_input()
    #         sleep(0.5)
    #         button[1].click_input()

    #         target_directory = Path(accepted_dir).parent.joinpath("chrome").resolve()

    #         target_directory.mkdir(exist_ok=True)
    #         source_directory = self.chr_dir

    #         try:
    #             comando = ["xcopy", source_directory, target_directory, "/E", "/H", "/C", "/I"]
    #             resultados = subprocess.run(  # nosec: B603
    #                 comando,
    #                 check=True,
    #                 text=True,
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #             )
    #             logger.info(str(resultados.stdout))

    #         except Exception as e:
    #             raise e

    #         with open(Path(accepted_dir), "w", encoding="utf-8") as f:  # noqa: FURB103
    #             f.write("")

    #     except Exception as e:
    #         raise e
