"""Módulo de tipos personalizados para o CrawJUD."""

import re
from collections import UserString
from contextlib import suppress
from typing import NoReturn

from crawjud.common.exceptions.validacao import ValidacaoStringError

PADRAO_CNJ: list[re.Pattern] = [r"^\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}$"]
PADRAO_DATA: list[re.Pattern] = [
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}Z$",
    r"^\d{4}-\d{2}-\d{2}"
    r"^\d{2}:\d{2}:\d{2}$",
    r"^\d{4}-\d{2}-\d{2}.\d{1,6}$",
]


def _raise_value_error() -> NoReturn:
    raise ValidacaoStringError(
        message="Valor informado não corresponde ao valor esperado",
    )


def _validate_str(seq: str, pattern_list: list[re.Pattern]) -> bool:
    validate_seq = any(re.match(pattern, seq) for pattern in pattern_list)

    if not validate_seq:
        _raise_value_error()


class StrTime[T](UserString):
    """Representa uma string de data/hora com validação de formatos específicos.

    Esta classe permite verificar se uma instância corresponde a padrões de data/hora
    definidos por expressões regulares.

    Args:
        instance (Any): Instância a ser verificada.

    Returns:
        bool: Indica se a instância corresponde a algum dos padrões de data/hora.

    """

    def __init__(self, seq: T) -> None:
        """Inicializa a classe StrTime."""
        _validate_str(seq, self.pattern_list)

        super().__init__(seq)

    def __str__(self) -> str:
        """Retorne a representação em string da instância StrTime.

        Returns:
            str: Representação textual da instância.

        """
        return self

    def __repr__(self) -> str:
        """Retorne a representação formal da instância StrTime.

        Returns:
            str: Representação formal da instância.

        """
        return self

    def __instancecheck__(self, instance: T) -> bool:
        """Verifique se a instância corresponde a padrões de data/hora definidos.

        Args:
            instance (T): Instância a ser verificada.

        Returns:
            bool: Indica se a instância corresponde a algum dos padrões de data/hora.

        """
        with suppress(ValueError):
            return _validate_str(instance, PADRAO_DATA)

        return False
        # Lista de padrões para validação de datas/horas


class StrProcessoCNJ[T](UserString):
    """Classe(str) StrProcessoCNJ para processos no padrão CNJ.

    Esta classe permite criar e verificar se o valor corresponde ao

    Args:
        instance (Any): Instância a ser verificada.

    Returns:
        bool: Indica se a instância corresponde a algum dos padrões de data/hora.

    """

    def __init__(self, seq: str) -> None:
        """Inicializa a classe StrTime."""
        _validate_str(seq, PADRAO_CNJ)

        seq = re.sub(
            r"(\d{7})(\d{2})(\d{4})(\d)(\d{2})(\d{4})",
            r"\1-\2.\3.\4.\5.\6",
            seq,
        )

        super().__init__(seq)

    @property
    def tj(self) -> str:
        """Extrai o ID do TJ.

        Returns:
            str: TJ ID

        """
        tj_id: str = re.search(r"(?<=5\.)\d{2}", self.data).group()
        if tj_id.startswith("0"):
            tj_id = tj_id.replace("0", "")

        return tj_id

    def __str__(self) -> str:
        """Retorne a representação em string da instância StrTime.

        Returns:
            str: Representação textual da instância.

        """
        return self.data

    def __repr__(self) -> str:
        """Retorne a representação formal da instância StrTime.

        Returns:
            str: Representação formal da instância.

        """
        return self

    def __instancecheck__(self, instance: T) -> bool:
        """Verifique se a instância corresponde a padrões de string CNJ.

        Args:
            instance (T): Instância a ser verificada.

        Returns:
            bool: Indica se a instância corresponde a algum dos padrões de string CNJ.

        """
        with suppress(ValueError):
            return _validate_str(instance, PADRAO_CNJ)

        return False
