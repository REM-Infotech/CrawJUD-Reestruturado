"""Realiza a busca e resolução de captcha de processos no sistema PJe.

Este módulo contém funções para buscar processos e resolver desafios captcha
utilizando dados fornecidos, integrando com tasks Celery e tratamento de exceções.
"""

from __future__ import annotations

import json.decoder
from typing import TYPE_CHECKING, Literal

from crawjud.controllers.bots.systems.pje import PjeBot
from crawjud.interface.types import BotData

if TYPE_CHECKING:
    from httpx import Client

    from crawjud.interface.types import BotData
    from crawjud.interface.types.pje import DictResults
# Expressão regular para validar URLs de processos PJe
pattern_url = (
    r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/"
    r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"
)


# Tipo literal para mensagem de processo não encontrado


class PJeSearch[T](PjeBot):
    """Classe de pesquisa PJe."""

    def search(  # noqa: D417
        self,
        data: BotData,
        row: int,
        client: Client,
        *args: T,
        **kwargs: T,
    ) -> DictResults | Literal["Nenhum processo encontrado"]:
        """Realize a busca de um processo no sistema PJe.

        Args:
            headers (dict[str, str]): Cabeçalhos HTTP para a requisição.
            cookies (dict[str, str]): Cookies HTTP para a requisição.
            data (BotData): Dados do processo a serem consultados.
            *args: Argumentos adicionais.
            **kwargs: Argumentos nomeados adicionais

        Returns:
            DictResults | Literal["Nenhum processo encontrado"]: Resultado da busca do
            processo ou mensagem indicando que nenhum processo foi encontrado.

        """
        # Envia mensagem de log para task assíncrona
        message = "Buscando processo {proc}".format(proc=data["NUMERO_PROCESSO"])
        self.print_msg(
            message=message,
            row=row,
            type_log="log",
        )
        link = f"/processos/dadosbasicos/{data['NUMERO_PROCESSO']}"
        response = client.get(url=link)
        id_processo: str

        if response.status_code == 403:
            return None

        try:
            data_request = response.json()

        except json.decoder.JSONDecodeError:
            return None

        # Caso a resposta seja uma lista, pega o primeiro item
        if isinstance(data_request, list):
            data_request: dict[str, T] = data_request[0]

        try:
            id_processo = data_request["id"]
        except KeyError:
            return None

        return self.desafio_captcha(
            data=data,
            row=row,
            id_processo=id_processo,
            client=client,
        )
