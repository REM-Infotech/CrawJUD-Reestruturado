"""
Realiza a busca e resolução de captcha de processos no sistema PJe.

Este módulo contém funções para buscar processos e resolver desafios captcha
utilizando dados fornecidos, integrando com tasks Celery e tratamento de exceções.
"""

from __future__ import annotations

import json.decoder
from typing import TYPE_CHECKING, Literal

from httpx import Client

from celery_app.addons.search import SearchController
from celery_app.types import BotData
from celery_app.types.pje import DictResults

if TYPE_CHECKING:
    from celery_app.types import BotData

# Expressão regular para validar URLs de processos PJe
pattern_url = r"^https:\/\/pje\.trt\d{1,2}\.jus\.br\/consultaprocessual\/detalhe-processo\/\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}\/\d+(#[a-zA-Z0-9]+)?$"


# Tipo literal para mensagem de processo não encontrado


class PJeSearch[T](SearchController):
    """Classe de pesquisa PJe."""

    def search(  # noqa: D417
        self,
        data: BotData,
        row: int,
        client: Client,
        *args: T,
        **kwargs: T,
    ) -> DictResults | Literal["Nenhum processo encontrado"]:
        """
        Realiza a busca de um processo no sistema PJe utilizando os dados fornecidos.

        Args:
            headers (dict[str, str]): Cabeçalhos HTTP para a requisição.
            cookies (dict[str, str]): Cookies HTTP para a requisição.
            data (BotData): Dados do processo a serem consultados.
            *args: Argumentos adicionais.
            **kwargs: Argumentos nomeados adicionais.

        Returns:
            resultado = desafio_captcha(id_processo=id_processo, data=data, url_base=url_base)

        Raises:
            ExecutionError: Caso ocorra erro ao obter informações do processo após múltiplas tentativas.

        """
        # Envia mensagem de log para task assíncrona
        message = "Buscando processo {proc}".format(proc=data["NUMERO_PROCESSO"])
        self.print_msg(
            message=message,
            row=row,
            type_log="log",
        )

        try:
            # Monta URL para buscar dados básicos do processo
            link = f"/processos/dadosbasicos/{data['NUMERO_PROCESSO']}"
            response = client.get(url=link)
            id_processo: str

            if response.status_code == 403:
                return

            try:
                data_request = response.json()

            except json.decoder.JSONDecodeError:
                return

            # Caso a resposta seja uma lista, pega o primeiro item
            if isinstance(data_request, list):
                data_request: dict[str, T] = data_request[0]

            try:
                id_processo = data_request["id"]
            except KeyError:
                return

            return self.desafio_captcha(
                data=data,
                row=row,
                id_processo=id_processo,
                client=client,
            )

        except Exception:
            self.print_msg("Erro ao buscar processo", row=row, type_log="error")
