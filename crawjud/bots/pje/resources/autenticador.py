# noqa: D100
from __future__ import annotations

import os
from time import sleep
from typing import Generic, TypeVar, cast

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from celery_app._wrapper import shared_task
from celery_app.custom._canvas import subtask
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types import ReturnFormataTempo
from crawjud.types.bot import DictReturnAuth, TReturnAuth
from utils.webdriver import DriverBot

T = TypeVar("AnyValue", bound=ReturnFormataTempo)


@shared_task(name="pje.autenticador")
def autenticar(regiao: str, *args: Generic[T], **kwargs: Generic[T]) -> TReturnAuth:  # noqa: D417
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
    driver = DriverBot(
        selected_browser="chrome",
        with_proxy=True,
    )
    wait = driver.wait

    try:
        url_login_task = subtask("pje.formata_url_pje").apply_async(
            kwargs={"regiao": regiao, "type_format": "login"}
        )
        url_valida_sessao_task = subtask("pje.formata_url_pje").apply_async(
            kwargs={"regiao": regiao, "type_format": "validate_login"}
        )

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

        try:
            WebDriverWait(driver, 60).until(ec.url_to_be(url_valida_sessao))
        except TimeoutException:
            return "Tempo de espera excedido para validação de sessão"

        sleep(1)

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
        driver.quit()
        raise ExecutionError(kwargs.get("pid", str(os.getpid())), e) from e
