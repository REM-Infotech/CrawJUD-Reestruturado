# noqa: D100
from __future__ import annotations

from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from celery_app._wrapper import shared_task
from crawjud.bots.pje.res.formatador import formata_url_pje
from webdriver import DriverBot


@shared_task(name="pje.autenticador")
def autenticar(  # noqa: D102, D103
    regiao: str,
) -> None:
    driver = DriverBot(
        selected_browser="chrome",
        with_proxy=True,
    )
    wait = driver.wait

    url = formata_url_pje(regiao)
    driver.get(url)
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

    WebDriverWait(driver, 60).until(
        ec.url_to_be(formata_url_pje(regiao, "validate_login"))
    )
