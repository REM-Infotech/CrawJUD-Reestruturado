"""
Realiza a busca e resolução de captcha de processos no sistema PJe.

Este módulo contém funções para buscar processos e resolver desafios captcha
utilizando dados fornecidos, integrando com tasks Celery e tratamento de exceções.
"""

from __future__ import annotations

from asyncio import sleep
from time import time
from typing import TYPE_CHECKING, Literal, cast

import requests as client
from celery import shared_task

from addons.recaptcha import captcha_to_image
from crawjud.exceptions.bot import ExecutionError
from crawjud.types import BotData
from crawjud.types.pje import DictDesafio, DictResults, DictReturnDesafio, Processo

if TYPE_CHECKING:
    from crawjud.types import BotData


# Expressão regular para validar URLs de processos PJe
pattern_url = r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"


# Tipo literal para mensagem de processo não encontrado
MessageNadaEncontrado = Literal["Nenhum processo encontrado"]


@shared_task(name="pje.buscador")
def buscar_processo(
    row: int,
    data: BotData,
    pid: str,
    url_base: str,
    start_time: str,
) -> DictReturnDesafio | MessageNadaEncontrado:
    """
    Realiza a busca de um processo no sistema PJe utilizando os dados fornecidos.

    Args:
        row (int): Número da linha do processo na lista de execução.
        data (BotData): Dados do processo a serem consultados.
        pid (str): Identificador do processo de execução.
        url_base (str): URL base do sistema PJe.
        start_time (str): Horário de início da execução.

    Returns:
        resultado = desafio_captcha(id_processo=id_processo, data=data, url_base=url_base)

    Raises:
        ExecutionError: Caso ocorra erro ao obter informações do processo após múltiplas tentativas.

    """
    # Envia mensagem de log para task assíncrona
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

    # Monta URL para buscar dados básicos do processo
    url_dados_basicos = f"/processos/dadosbasicos/{data['NUMERO_PROCESSO']}"
    link = f"{url_base}/{url_dados_basicos}".replace("//", "/")
    response = client.get(url=link, timeout=10)
    data_request = response.json()

    # Caso a resposta seja uma lista, pega o primeiro item
    if isinstance(data_request, list):
        data_request = data_request[0]

    # Se encontrou o id do processo, resolve o captcha
    if data_request.get("id"):
        id_processo = str(data_request["id"])
        resultado = desafio_captcha(
            id_processo=id_processo, data=data, url_base=url_base
        )
        return cast(DictReturnDesafio, resultado)

    # Caso não encontre, retorna mensagem padrão
    return "Nenhum processo encontrado"


def desafio_captcha(
    id_processo: str, data: BotData, url_base: str
) -> DictReturnDesafio:
    """
    Resolve o desafio captcha para acessar informações do processo no sistema PJe.

    Args:
        id_processo (str): Identificador do processo a ser consultado.
        data (BotData): Dados do bot necessários para a requisição.
        url_base (str): URL base do sistema PJe.

    Returns:
        DictReturnDesafio: Dicionário contendo headers, cookies e resultados do processo.

    Raises:
        ExecutionError: Caso não seja possível obter informações do processo após 15 tentativas.

    """
    tries: int = 0
    response2 = None
    results: DictResults = {}
    # Monta URL para obter o desafio captcha
    url_desafio = f"/captcha?idProcesso={id_processo}"
    link = f"{url_base}/{url_desafio}".replace("//", "/")

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

        url = f"/processos/{id_processo}?tokenDesafio={token_desafio}&resposta={text}"
        link_desafio = f"{url_base}/{url}".replace("//", "/")

        response2 = client.get(url=link_desafio, timeout=60)
        sleep(int(2 + (int(time()) % 11)))

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
            break

        img = data_request.get("imagem")
        token_desafio = data_request.get("tokenDesafio")
        tries += 1

    # Se exceder o número de tentativas, lança exceção
    if tries > 15:
        raise ExecutionError("", message="Erro ao obter informações do processo")

    return_data = cast(
        DictReturnDesafio,
        {
            "headers": dict(response2.headers),
            "cookies": response2.cookies.get_dict(),
            "results": results,
        },
    )

    return return_data
