from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Literal, TypeVar

from crawjud.types.bot import BotData, MessageNadaEncontrado
from crawjud.types.pje import DictReturnDesafio

T = TypeVar("Class", bound=object)


func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}


class AbstractClassBot(ABC):  # noqa: D101
    @classmethod
    def __subclasshook__(cls, C: T) -> NotImplementedError | Literal[True]:  # noqa: D105, N803
        if cls is AbstractClassBot:
            subclass_functions = func_dict_check[cls.subclass_type]

            for item in subclass_functions:
                if any(item in B.__dict__ for B in C.__mro__):
                    return True

        return True
        # return NotImplementedError("Função não implementada!")

    @abstractmethod
    def buscar_processo(  # noqa: D102
        self,
        data: BotData,
        headers: dict[str, str],
        cookies: dict[str, str],
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> DictReturnDesafio | MessageNadaEncontrado:
        return NotImplementedError("Função não implementada!")

    @abstractmethod
    def execution(self, *args: Generic[T], **kwargs: Generic[T]) -> None:  # noqa: D102
        return NotImplementedError("Função não implementada!")

    def print_msg(  # noqa: D417
        self,
        pid: str,
        message: str,
        row: int,
        type_log: str,
        total_rows: int,
        start_time: str,
        errors: int = 0,
        status: str = "Em Execução",
    ) -> None:
        """
        Envia mensagem de log para o sistema de tarefas assíncronas.

        Args:
            pid (str): Identificador do processo.
            message (str): Mensagem a ser registrada.
            row (int): Linha atual do processamento.
            type_log (str): Tipo de log (info, error, etc).
            total_rows (int): Total de linhas a serem processadas.
            start_time (str): Horário de início do processamento.
            status (str): Status atual do processamento (default: "Em Execução").

        Returns:
            None: Não retorna valor.

        """
        return NotImplementedError("Função não implementada!")

    def elawFormats(  # noqa: N802
        self, data: dict[str, str], cities_amazonas: dict[str, Any]
    ) -> dict[str, str]:
        """Format a legal case dictionary according to pre-defined rules.

        Args:
            data (dict[str, str]): The raw data dictionary.
            cities_amazonas: Dicionario com as cidades do estado do Amazonas.

        Returns:
            dict[str, str]: The data formatted with proper types and values.

        :Rules:
            :
                - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
                - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
                - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
                - If the value is an integer or float, format it to two decimal places and replace the decimal point with a clcomma.
                - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".

        """
        return NotImplementedError("Função não implementada!")

    def save_success_cache(self, data: dict) -> None:  # noqa: D102
        return NotImplementedError("Função não implementada!")
