"""Módulo de controle de autenticação Pje."""

from time import sleep

from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud_app.addons.auth import AuthController
from crawjud_app.common.exceptions.bot import LoginSystemError
from utils.webdriver import DriverBot


class PjeAuth(AuthController):
    """Classe de autenticação PJE."""

    def auth(self) -> bool:  # noqa: D102
        try:
            driver = DriverBot(
                selected_browser="chrome",
                with_proxy=True,
            )

            wait = driver.wait
            url_login = self.formata_url_pje(_format="login")
            url_valida_sessao = self.formata_url_pje(_format="validate_login")

            driver.get(url_login)
            btn_sso = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'button[id="btnSsoPdpj"]',
                )),
            )
            btn_sso.click()

            sleep(5)

            btn_certificado = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ('div[class="certificado"] > a'),
                )),
            )
            event_cert = btn_certificado.get_attribute("onclick")
            driver.execute_script(event_cert)
            sleep(1)
            try:
                WebDriverWait(
                    driver=driver,
                    timeout=15,
                    poll_frequency=0.3,
                    ignored_exceptions=(UnexpectedAlertPresentException),
                ).until(ec.url_to_be(url_valida_sessao))
            except TimeoutException:
                if "pjekz" not in driver.current_url:
                    return False

            if (
                "pjekz/painel/usuario-externo" in driver.current_url
                or "pjekz" in driver.current_url
            ):
                driver.refresh()

            cookies_driver = driver.get_cookies()
            har_data_ = driver.current_HAR
            entries = list(har_data_.entries)
            entry_proxy = [
                item
                for item in entries
                if f"https://pje.trt{self.regiao}.jus.br/pje-comum-api/"
                in item.request.url
            ][-1]

            cookies_ = {
                str(cookie["name"]): str(cookie["value"]) for cookie in cookies_driver
            }

            headers_ = {
                str(header["name"]): str(header["value"])
                for header in entry_proxy.request.headers
            }

            self._cookies = cookies_
            self._headers = headers_
            self._base_url = (
                f"https://pje.trt{self.regiao}.jus.br/pje-consulta-api/api"
            )

        except LoginSystemError:
            self.print_msg("Erro ao realizar autenticação", type_log="error")
            return False

        return True
