from __future__ import annotations

from abc import ABC, abstractmethod  # noqa: F401
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar  # noqa: F401

from pytz import timezone

from celery_app.types.bot import BotData, MessageNadaEncontrado  # noqa: F401
from celery_app.types.pje import Resultados  # noqa: F401
from utils.models.logs import MessageLogDict

func_dict_check = {
    "bot": ["execution"],
    "search": ["buscar_processo"],
}

if TYPE_CHECKING:
    from celery_app.addons.auth.controller import AuthController
    from celery_app.addons.search.controller import SearchController


class AbstractClassBot[T](ABC):  # noqa: B024, D101
    tasks_cls = {}
    subclasses_auth: dict[str, type[AuthController]] = {}
    subclasses_search: dict[str, type[SearchController]] = {}
    # Atributos Globais
    _pid: str = None
    _total_rows: int = 0
    _start_time: str = None
    _regiao: str = None
    _data_regiao: list[BotData]
    _cookies: dict[str, str]
    _headers: dict[str, str]
    _base_url: str

    @property
    def data_regiao(self) -> list[BotData]:
        return self._data_regiao

    @data_regiao.setter
    def data_regiao(self, _data_regiao: str) -> None:
        self._data_regiao = _data_regiao

    @property
    def regiao(self) -> str:
        return self._regiao

    @regiao.setter
    def regiao(self, _data_regiao: str) -> None:
        self._data_regiao = _data_regiao

    def print_msg(  # noqa: D417
        self,
        message: str,
        row: int = 0,
        errors: int = 0,
        type_log: str = "log",
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
        # Obtém o horário atual formatado
        time_exec = datetime.now(tz=timezone("America/Manaus")).strftime("%H:%M:%S")
        # Monta o prompt da mensagem
        prompt = (
            f"[({self._pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"
        )

        # Cria objeto de log da mensagem
        data = {
            "data": MessageLogDict(
                message=str(prompt),
                pid=str(self._pid),
                row=int(row),
                type=type_log,
                status="Em Execução",
                total=int(self._total_rows),
                success=0,
                errors=errors,
                remaining=int(self._total_rows),
                start_time=self._start_time,
            )
        }

        self.sio.emit(
            event="log_execution",
            data=data,
        )
        # Envia a mensagem formatada para o sistema de monitoramento

    @classmethod
    def __subclasshook__(cls, C: T) -> NotImplementedError | Literal[True]:  # noqa: D105, N803
        if cls is AbstractClassBot:
            subclass_functions = func_dict_check[cls.subclass_type]

            for item in subclass_functions:
                if any(item in B.__dict__ for B in C.__mro__):
                    return True

        return True
        # return NotImplementedError("Função não implementada!")

    def __init_subclass__(cls) -> None:  # noqa: D105
        cls.tasks_cls[cls.__name__] = cls

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
