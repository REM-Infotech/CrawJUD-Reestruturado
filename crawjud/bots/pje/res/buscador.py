"""
Realiza a busca e resolução de captcha de processos no sistema PJe.

Este módulo contém funções para buscar processos e resolver desafios captcha
utilizando dados fornecidos, integrando com tasks Celery e tratamento de exceções.
"""

from __future__ import annotations

import json.decoder
from time import sleep
from typing import TYPE_CHECKING, cast

from celery import shared_task
from httpx import Client

from addons.recaptcha import captcha_to_image
from celery_app.custom._canvas import subtask
from crawjud.common.exceptions.bot import ExecutionError
from crawjud.types import BotData
from crawjud.types.bot import MessageNadaEncontrado
from crawjud.types.pje import DictDesafio, DictResults, DictReturnDesafio, Processo

if TYPE_CHECKING:
    from crawjud.types import BotData


# Expressão regular para validar URLs de processos PJe
pattern_url = r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"


# Tipo literal para mensagem de processo não encontrado


@shared_task(name="pje.buscador")
def buscar_processo(
    data: BotData,
    headers: dict[str, str],
    cookies: dict[str, str],
) -> DictReturnDesafio | MessageNadaEncontrado:
    """
    Realiza a busca de um processo no sistema PJe utilizando os dados fornecidos.

    Args:
        headers (dict[str, str]): Cabeçalhos HTTP para a requisição.
        cookies (dict[str, str]): Cookies HTTP para a requisição.
        data (BotData): Dados do processo a serem consultados.

    Returns:
        resultado = desafio_captcha(id_processo=id_processo, data=data, url_base=url_base)

    Raises:
        ExecutionError: Caso ocorra erro ao obter informações do processo após múltiplas tentativas.

    """
    # Envia mensagem de log para task assíncrona

    pid = str(data["pid"])
    row = int(data["row"])
    url_base = str(data["url_base"])
    start_time = data["start_time"]
    task_message = subtask("log_message")
    task_message.apply_async(
        kwargs={
            "pid": pid,
            "message": f"Buscando processo {data['NUMERO_PROCESSO']}",
            "row": row,
            "type_log": "log",
            "total_rows": data.get("total_rows", 0),
            "start_time": start_time,
        }
    )

    with Client(
        base_url=url_base,
        timeout=30,
        headers=headers,
        cookies=cookies,
    ) as client:
        # Monta URL para buscar dados básicos do processo
        url_dados_basicos = f"/processos/dadosbasicos/{data['NUMERO_PROCESSO']}"
        response = client.get(url=url_dados_basicos)

        try:
            data_request = response.json()

        except json.decoder.JSONDecodeError:
            data_request = response.content
            print(f"\n\n\n\n{data_request}\n\n\n\n")
            return "Nenhum processo encontrado"

        # Caso a resposta seja uma lista, pega o primeiro item
        if isinstance(data_request, list):
            data_request = data_request[0]

        # Se encontrou o id do processo, resolve o captcha
        if data_request.get("id"):
            id_processo = str(data_request["id"])
            resultado = desafio_captcha(
                data=data, id_processo=id_processo, client=client
            )
            return cast(DictReturnDesafio, resultado)

        # Caso não encontre, retorna mensagem padrão
        return "Nenhum processo encontrado"


def desafio_captcha(
    data: BotData, id_processo: str, client: Client
) -> DictReturnDesafio:
    """
    Resolve o desafio captcha para acessar informações do processo no sistema PJe.

    Args:
        data (BotData): Dados do processo a serem consultados.
        id_processo (str): Identificador do processo a ser consultado.
        client (Client): Cliente HTTP para realizar requisições.

    Returns:
        DictReturnDesafio: Dicionário contendo headers, cookies e resultados do processo.

    Raises:
        ExecutionError: Caso não seja possível obter informações do processo após 15 tentativas.

    """
    tries: int = 0
    response2 = None
    results: DictResults = {}
    # Monta URL para obter o desafio captcha
    link = f"/captcha?idProcesso={id_processo}"
    response = client.get(url=link, timeout=60)
    _request_json = response.json()

    # Caso a resposta seja uma lista, pega o último item
    if isinstance(_request_json, list):
        _request_json = _request_json[-1]

    data_request: DictDesafio = cast(DictDesafio, _request_json)
    token_desafio = data_request.get("tokenDesafio")
    img = (
        data_request.get("imagem")
        .replace(" ", "")
        .replace("data:image/png;base64,", "")
    )
    # Tenta resolver o captcha até 15 vezes
    while tries < 15:
        text = captcha_to_image(img)

        _link2 = (
            f"/processos/{id_processo}?tokenDesafio={token_desafio}&resposta={text}"
        )

        response2 = client.get(url=_link2, timeout=60)

        data_request = response2.json()
        # Se não retornar imagem, captcha foi resolvido
        if not data_request.get("imagem"):
            results = DictResults(
                id_processo=id_processo,
                captchatoken=response2.headers.get("captchatoken", ""),
                text=text,
                data_request=cast(Processo, data_request),
            )
            tries = 0
            pid = str(data["pid"])
            row = int(data["row"])
            start_time = data["start_time"]
            task_message = subtask("log_message")
            task_message.apply_async(
                kwargs={
                    "pid": pid,
                    "message": f"Processo {data['NUMERO_PROCESSO']} encontrado! Salvando dados...",
                    "row": row,
                    "type_log": "info",
                    "total_rows": data.get("total_rows", 0),
                    "start_time": start_time,
                }
            )
            break

        sleep(4)
        img = data_request.get("imagem")
        token_desafio = data_request.get("tokenDesafio")
        tries += 1

    # Se exceder o número de tentativas, lança exceção
    if tries > 15:
        raise ExecutionError("", message="Erro ao obter informações do processo")

    _cookies: dict[str, str] = {}

    for cookie in response2._request.headers["Cookie"].split("; "):  # noqa: SLF001
        key, value = cookie.split("=", 1)
        _cookies[key] = value

    return_data = cast(
        DictReturnDesafio,
        {
            "headers": dict(response2.headers),
            "cookies": dict(_cookies),
            "results": results,
        },
    )

    return return_data
