# noqa: D100
from __future__ import annotations

from asyncio import sleep
from typing import TYPE_CHECKING

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from crawjud.bots.pje.res.formatador import formata_url_pje
from crawjud.core._dictionary import BotData

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


async def autenticar(  # noqa: D102, D103
    driver: WebDriver, wait: WebDriverWait, regiao: str, data: BotData = None
) -> None:
    url = await formata_url_pje(regiao)
    driver.get(url)
    btn_sso = wait.until(
        ec.presence_of_element_located((
            By.CSS_SELECTOR,
            'button[id="btnSsoPdpj"]',
        ))
    )
    btn_sso.click()

    await sleep(5)

    btn_certificado = wait.until(
        ec.presence_of_element_located((
            By.CSS_SELECTOR,
            ('div[class="certificado"] > a'),
        ))
    )
    event_cert = btn_certificado.get_attribute("onclick")
    driver.execute_script(event_cert)

    WebDriverWait(driver, 60).until(
        ec.url_to_be(await formata_url_pje(regiao, "validate_login"))
    )
