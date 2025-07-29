# noqa: D100
import base64
import io
import re
from asyncio import sleep
from contextlib import suppress
from typing import TYPE_CHECKING, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from addons.recaptcha import captcha_to_image
from crawjud.bots.pje.res.formatador import formata_url_pje
from crawjud.core._dictionary import BotData

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


pattern_url = r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"


async def buscar_processo(  # noqa: D102, D103
    row: int,
    driver: WebDriver,
    wait: WebDriverWait,
    data: BotData,
    regiao: str,
    print_msg: Any,
    pid: str,
) -> None:
    url = await formata_url_pje(regiao, "search")
    driver.get(url)
    print_msg(
        message=f"Buscando processo Nº{data['NUMERO_PROCESSO']}",
        pid=pid,
        row=row,
        type_log="log",
        status="Em Execução",
    )
    campo_processo = wait.until(
        ec.presence_of_element_located((
            By.CSS_SELECTOR,
            'input[id="nrProcessoInput"]',
        ))
    )

    campo_processo.click()
    campo_processo.send_keys(data["NUMERO_PROCESSO"])

    btn_pesquisar = wait.until(
        ec.presence_of_element_located((
            By.CSS_SELECTOR,
            'button[id="btnPesquisar"]',
        ))
    )
    btn_pesquisar.click()
    await desafio_captcha(driver, wait)
    print_msg(
        message="Processo encontrado!",
        row=row,
        type_log="info",
        pid=pid,
        status="Em Execução",
    )


async def desafio_captcha(  # noqa: D102, D103
    driver: WebDriver,
    wait: WebDriverWait,
) -> None:
    tries = 0

    with suppress(Exception):
        btn_proc = WebDriverWait(driver, 5).until(
            ec.presence_of_all_elements_located((
                By.CSS_SELECTOR,
                'button[class="selecao-processo ng-star-inserted"]',
            ))
        )[0]
        btn_proc.click()

    while tries < 15:
        with suppress(Exception):
            img = wait.until(
                ec.presence_of_element_located((
                    By.CSS_SELECTOR,
                    'img[id="imagemCaptcha"]',
                ))
            ).get_attribute("src")
            bytes_img = base64.b64decode(
                img.replace(" ", "").replace("data:image/png;base64,", "")
            )
            readable_buffer = io.BytesIO(bytes_img)
            text = captcha_to_image(readable_buffer.read()).zfill(6)[:6]

            input_captcha = driver.find_element(
                By.CSS_SELECTOR, 'input[id="captchaInput"]'
            )
            input_captcha.send_keys(text)

            btn_enviar = driver.find_element(
                By.CSS_SELECTOR, 'button[id="btnEnviar"]'
            )
            btn_enviar.click()

        await sleep(2)
        full_match = re.fullmatch(pattern_url, driver.current_url)

        if full_match:
            break

        tries += 1
