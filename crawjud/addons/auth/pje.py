"""Módulo de controle de autenticação Pje."""

import os
from contextlib import suppress
from time import sleep
from typing import cast

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from celery_app.types._celery._canvas import AsyncResult
from crawjud.addons.auth import AuthController
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types.bot import DictReturnAuth, TReturnAuth
from utils.webdriver import DriverBot


def url_task(regiao: str, type_format: str) -> AsyncResult | None:  # noqa: D103
    return subtask("pje.formata_url_pje").apply_async(
        kwargs={"regiao": regiao, "type_format": type_format}
    )


@shared_task(name="pje.autenticador")
def autenticar[T](regiao: str, *args: T, **kwargs: T) -> TReturnAuth:  # noqa: D417
    r"""
    Realiza a autenticação no sistema PJe utilizando certificado digital.

    Args:
        regiao (str): Região do tribunal para autenticação.

    Returns:
        (TReturnAuth | MessageTimeoutAutenticacao):
            `TReturnAuth`: Dicionário contendo cookies, headers e base_url autenticados.

            `MessageTimeoutAutenticacao`: Mensagem de erro caso o tempo de espera para validação de sessão seja excedido.

    Raises:
        TimeoutException: Caso ocorra um timeout ao procurar elementos na página.

    """
    try:
        driver = DriverBot(
            selected_browser="chrome",
            with_proxy=True,
        )
        wait = driver.wait

        url_login_task = url_task(regiao=regiao, type_format="login")
        url_valida_sessao_task = url_task(regiao=regiao, type_format="validate_login")

        url_login: str = url_login_task.wait_ready()
        url_valida_sessao: str = url_valida_sessao_task.wait_ready()

        driver.get(url_login)
        btn_sso = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                'button[id="btnSsoPdpj"]',
            ))
        )
        btn_sso.click()

        sleep(5)

        btn_certificado = wait.until(
            ec.presence_of_element_located((
                By.CSS_SELECTOR,
                ('div[class="certificado"] > a'),
            ))
        )
        event_cert = btn_certificado.get_attribute("onclick")
        driver.execute_script(event_cert)
        sleep(1)
        try:
            WebDriverWait(driver, 15).until(ec.url_to_be(url_valida_sessao))
        except TimeoutException:
            if "pjekz" not in driver.current_url:
                return "Tempo de espera excedido para validação de sessão"

        if (
            "pjekz/painel/usuario-externo" in driver.current_url
            or "pjekz" in driver.current_url
        ):
            driver.refresh()

        cookies_driver = driver.get_cookies()
        _har_data = driver.current_HAR
        entries = list(_har_data.entries)
        entry_proxy = [
            item
            for item in entries
            if f"https://pje.trt{regiao}.jus.br/pje-comum-api/" in item.request.url
        ][-1]

        _cookies = {
            str(cookie["name"]): str(cookie["value"]) for cookie in cookies_driver
        }

        _headers = {
            str(header["name"]): str(header["value"])
            for header in entry_proxy.request.headers
        }
        driver.quit()

        return cast(
            DictReturnAuth,
            {
                "cookies": _cookies,
                "headers": _headers,
                "base_url": f"https://pje.trt{regiao}.jus.br/pje-consulta-api/api",
            },
        )

    except Exception as e:
        with suppress(Exception):
            driver.quit()

        raise ExecutionError(kwargs.get("pid", str(os.getpid())), e) from e


class PjeAuth(AuthController):
    """Classe de autenticação PJE."""

    def auth(self) -> bool:  # noqa: D102
        try:
            task_autenticacao = subtask("pje.autenticador")
            autenticacao_data: TReturnAuth = task_autenticacao.apply_async(
                kwargs={"regiao": self.regiao}
            ).wait_ready()

            if not isinstance(autenticacao_data, dict):
                message_erro = "Erro ao realizar autenticação"
                if str(autenticacao_data):
                    message_erro = str(autenticacao_data)

                self.print_msg(
                    message=message_erro,
                    type_log="error",
                    errors=len(self.data_regiao),
                )
                return False

            self._cookies = autenticacao_data["cookies"]
            self._base_url = autenticacao_data["base_url"]
            self._headers = autenticacao_data["headers"]

            return True

            # self.driver.get(self.elements.url_login)

            # login = self.wait.until(
            #     ec.presence_of_element_located((
            #         By.CSS_SELECTOR,
            #         self.elements.login_input,
            #     ))
            # )
            # password = self.wait.until(
            #     ec.presence_of_element_located((
            #         By.CSS_SELECTOR,
            #         self.elements.password_input,
            #     ))
            # )
            # entrar = self.wait.until(
            #     ec.presence_of_element_located((
            #         By.CSS_SELECTOR,
            #         self.elements.btn_entrar,
            #     ))
            # )

            # login.send_keys(self.username)
            # sleep(0.5)
            # password.send_keys(self.password)
            # sleep(0.5)
            # entrar.click()

            # logado = None
            # with suppress(TimeoutException):
            #     logado = WebDriverWait(self.driver, 10).until(
            #         ec.url_to_be(self.elements.chk_login)
            #     )

            # return logado is not None

        except Exception as e:
            raise e
