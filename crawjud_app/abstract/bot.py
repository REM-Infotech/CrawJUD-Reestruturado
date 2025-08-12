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
    @abstractmethod
    def execution(self) -> None: ...  # noqa: D102

    def elaw_formats(
        self,
        data: dict[str, str],
        cities_amazonas: dict[str, AnyStr],
    ) -> dict[str, str]:
        """Formata um dicionário de processo jurídico conforme regras pré-definidas.

        Args:
            data (dict[str, str]): Dicionário de dados brutos.
            cities_amazonas (dict[str, AnyStr]): Dicionário das cidades do Amazonas.

        Returns:
            (dict[str, str]): Dados formatados com tipos e valores adequados.

        Examples:
            - Remove chaves com valores vazios ou None.
            - Atualiza "TIPO_PARTE_CONTRARIA" se "TIPO_EMPRESA" for "RÉU".
            - Atualiza "CAPITAL_INTERIOR" conforme "COMARCA".
            - Define "DATA_INICIO" se ausente e "DATA_LIMITE" presente.
            - Formata valores numéricos para duas casas decimais.
            - Define "CNPJ_FAVORECIDO" padrão se vazio.

        """
        # Remove chaves com valores vazios ou None
        self._remove_empty_keys(data)

        # Atualiza "TIPO_PARTE_CONTRARIA" se necessário
        self._update_tipo_parte_contraria(data)

        # Atualiza "CAPITAL_INTERIOR" conforme "COMARCA"
        self._update_capital_interior(data, cities_amazonas)

        # Define "DATA_INICIO" se ausente e "DATA_LIMITE" presente
        self._set_data_inicio(data)

        # Formata valores numéricos
        self._format_numeric_values(data)

        # Define "CNPJ_FAVORECIDO" padrão se vazio
        self._set_default_cnpj(data)

        return data

    def _remove_empty_keys(self, data: dict[str, str]) -> None:
        """Remove chaves com valores vazios ou None."""
        dict_data = data.copy()
        for key in dict_data:
            value = dict_data[key]
            if (isinstance(value, str) and not value.strip()) or value is None:
                data.pop(key)

    def _update_tipo_parte_contraria(self, data: dict[str, str]) -> None:
        """Atualiza 'TIPO_PARTE_CONTRARIA' se 'TIPO_EMPRESA' for 'RÉU'."""
        tipo_empresa = data.get("TIPO_EMPRESA", "").upper()
        if tipo_empresa == "RÉU":
            data["TIPO_PARTE_CONTRARIA"] = "Autor"

    def _update_capital_interior(
        self,
        data: dict[str, str],
        cities_amazonas: dict[str, AnyStr],
    ) -> None:
        """Atualiza 'CAPITAL_INTERIOR' conforme 'COMARCA'."""
        comarca = data.get("COMARCA")
        if comarca:
            set_locale = cities_amazonas.get(comarca, "Outro Estado")
            data["CAPITAL_INTERIOR"] = set_locale

    def _set_data_inicio(self, data: dict[str, str]) -> None:
        """Define 'DATA_INICIO' se ausente e 'DATA_LIMITE' presente."""
        if "DATA_LIMITE" in data and not data.get("DATA_INICIO"):
            data["DATA_INICIO"] = data["DATA_LIMITE"]

    def _format_numeric_values(self, data: dict[str, str]) -> None:
        """Formata valores numéricos para duas casas decimais."""
        loop_data = data.items()
        for key, value in loop_data:
            if isinstance(value, (int, float)):
                data[key] = f"{value:.2f}".replace(".", ",")

    def _set_default_cnpj(self, data: dict[str, str]) -> None:
        """Define 'CNPJ_FAVORECIDO' padrão se vazio."""
        if not data.get("CNPJ_FAVORECIDO"):
            data["CNPJ_FAVORECIDO"] = "04.812.509/0001-90"
