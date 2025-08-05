"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    AnyStr,
    ParamSpec,
    TypeVar,
)

from dotenv import dotenv_values

from celery_app.custom._canvas import subtask

T = TypeVar("AnyValue", bound=str)
PrintParamSpec = ParamSpec("PrintParamSpec", bound=str)
PrintTReturn = TypeVar("PrintTReturn", bound=Any)

environ = dotenv_values()

TReturn = TypeVar("TReturn")


class ClassBot(ABC):  # noqa:  D101
    @abstractmethod
    def execution(self) -> None: ...  # noqa: D102

    @abstractmethod
    def queue(self) -> None: ...  # noqa: D102

    def print_msg(
        self,
        pid: str,
        message: str,
        row: int,
        type_log: str,
        total_rows: int,
        start_time: str,
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

        Returns:
            None: Não retorna valor.

        """
        _task_message = subtask("log_message")
        _task_message.apply_async(
            kwargs={
                "pid": pid,
                "message": message,
                "row": row,
                "type_log": type_log,
                "total_rows": total_rows,
                "start_time": start_time,
            }
        )

    def elawFormats(  # noqa: N802
        self, data: dict[str, str], cities_amazonas: dict[str, AnyStr]
    ) -> dict[str, str]:
        """Format a legal case dictionary according to pre-defined rules.

        Args:
            data (dict[str, str]): The raw data dictionary.
            cities_amazonas: Dicionario com as cidades do estado do Amazonas.

        Returns:
            dict[str, str]: The data formatted with proper types and values.

        Rules:
            - If the key is "TIPO_EMPRESA" and its value is "RÉU", update "TIPO_PARTE_CONTRARIA" to "Autor".
            - If the key is "COMARCA", update "CAPITAL_INTERIOR" based on the value using the cities_Amazonas method.
            - If the key is "DATA_LIMITE" and "DATA_INICIO" is not present, set "DATA_INICIO" to the value of "DATA_LIMITE".
            - If the value is an integer or float, format it to two decimal places and replace the decimal point with a clcomma.
            - If the key is "CNPJ_FAVORECIDO" and its value is empty, set it to "04.812.509/0001-90".

        """  # noqa: E501
        data_listed = list(data.items())
        for key, value in data_listed:
            if isinstance(value, str):
                if not value.strip():
                    data.pop(key)

            elif value is None:
                data.pop(key)

            if key.upper() == "TIPO_EMPRESA":
                data["TIPO_PARTE_CONTRARIA"] = "Autor"
                if value.upper() == "RÉU":
                    data["TIPO_PARTE_CONTRARIA"] = "Autor"

            elif key.upper() == "COMARCA":
                set_locale = cities_amazonas.get(value, "Outro Estado")
                data["CAPITAL_INTERIOR"] = set_locale

            elif key == "DATA_LIMITE" and not data.get("DATA_INICIO"):
                data["DATA_INICIO"] = value

            elif isinstance(value, (int, float)):
                data[key] = f"{value:.2f}".replace(".", ",")

            elif key == "CNPJ_FAVORECIDO" and not value:
                data["CNPJ_FAVORECIDO"] = "04.812.509/0001-90"

        return data
