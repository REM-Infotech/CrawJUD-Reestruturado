"""Módulo de tipos personalizados para o CrawJUD."""

import re
from collections import UserString


class StrTime[T](UserString):
    """Representa uma string de data/hora com validação de formatos específicos.

    Esta classe permite verificar se uma instância corresponde a padrões de data/hora
    definidos por expressões regulares.

    Args:
        instance (Any): Instância a ser verificada.

    Returns:
        bool: Indica se a instância corresponde a algum dos padrões de data/hora.

    """

    __slots__ = ()

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
        # Lista de padrões para validação de datas/horas
        pattern_list = [
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}$",
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}Z$",
            r"^\d{4}-\d{2}-\d{2}"
            r"^\d{2}:\d{2}:\d{2}$",
            r"^\d{4}-\d{2}-\d{2}.\d{1,6}$",
        ]

        return any(re.match(pattern, instance) for pattern in pattern_list)
