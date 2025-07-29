# noqa: D100
import base64
import io
from asyncio import sleep
from time import time
from typing import TYPE_CHECKING, Any

import httpx

from addons.recaptcha import captcha_to_image
from crawjud.core._dictionary import BotData
from crawjud.exceptions.bot import ExecutionError

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData


pattern_url = r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"


async def buscar_processo(  # noqa: D102, D103
    row: int,
    client: httpx.AsyncClient,
    data: BotData,
    print_msg: Any,
    pid: str,
) -> tuple[
    httpx.Headers, httpx.Cookies, str, tuple[str, str, str, dict[str, str | Any]]
]:
    print_msg(
        message=f"Buscando processo Nº{data['NUMERO_PROCESSO']}",
        pid=pid,
        row=row,
        type_log="log",
        status="Em Execução",
    )
    url_dados_basicos = f"/processos/dadosbasicos/{data['NUMERO_PROCESSO']}"
    response = await client.get(url=url_dados_basicos)
    data_request: dict[str, str] = response.json()

    if isinstance(data_request, list):
        data_request = data_request[0]

    id_processo = str(data_request[0]["id"])

    resultado = await desafio_captcha(
        client=client, id_processo=id_processo, data=data
    )

    print_msg(
        message="Processo encontrado!",
        row=row,
        type_log="info",
        pid=pid,
        status="Em Execução",
    )
    return resultado


async def desafio_captcha(  # noqa: D102, D103
    client: httpx.AsyncClient,
    id_processo: str,
    data: BotData,
) -> tuple[
    httpx.Headers, httpx.Cookies, str, tuple[str, str, str, dict[str, str | Any]]
]:
    tries = 0
    response2 = None
    results: tuple[str, str, str, dict[str, str | Any]] = None
    url_desafio = f"/captcha?idProcesso={id_processo}"
    response = await client.get(url=url_desafio)
    data_request: dict[str, str] = response.json()

    if isinstance(data_request, list):
        data_request = data_request[-1]

    img = data_request.get("imagem")
    token_desafio = data_request.get("tokenDesafio")

    while tries < 15:
        bytes_img = base64.b64decode(
            img.replace(" ", "").replace("data:image/png;base64,", "")
        )
        readable_buffer = io.BytesIO(bytes_img)
        text = captcha_to_image(readable_buffer.read()).zfill(6)[:6]
        url = f"/processos/{id_processo}?tokenDesafio={token_desafio}&resposta={text}"

        response2 = await client.get(url=url)
        now = int(time())
        sleep_time = 2 + (now % 11)  # 2 a 15 segundos
        await sleep(sleep_time)

        data_request: dict[str, str] = response2.json()
        if not data_request.get("imagem"):
            results = (
                id_processo,
                response2.headers["captchatoken"],
                text,
                data_request,
            )
            tries = 0
            break

        img = data_request.get("imagem")
        token_desafio = data_request.get("tokenDesafio")
        tries += 1

    if tries > 15:
        raise ExecutionError("", message="Erro ao obter informações do processo")

    return response2.headers, response2.cookies, results
