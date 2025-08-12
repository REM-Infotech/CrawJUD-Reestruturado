"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

from abc import abstractmethod
from typing import (
    AnyStr,
    ParamSpec,
)

from dotenv import dotenv_values

from crawjud_app.abstract._head import HeadBot

PrintParamSpec = ParamSpec("PrintParamSpec", bound=str)

environ = dotenv_values()


class ClassBot[T](HeadBot):  # noqa:  D101
    def __init__(self) -> None:  # noqa: D107
        print("ok")

    @abstractmethod
    def execution(self) -> None: ...  # noqa: D102

    def elaw_formats(
        self,
        data: dict[str, str],
        cities_amazonas: dict[str, AnyStr],
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
