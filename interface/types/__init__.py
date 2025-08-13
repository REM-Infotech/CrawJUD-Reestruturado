"""Defina tipos e aliases utilizados em toda a aplicação CrawJUD.

Este módulo centraliza definições de tipos, facilitando a tipagem
de dados, parâmetros e retornos em funções e classes do projeto.

"""

import re
from collections import UserString
from datetime import datetime, timedelta
from os import PathLike
from typing import Literal, TypeVar

from interface.types.bot import BotData

TReturnMessageMail = Literal["E-mail enviado com sucesso!"]
TReturnMessageExecutBot = Literal["Execução encerrada com sucesso!"]
TReturnMessageUploadFile = Literal["Arquivo enviado com sucesso!"]
Numbers = int | float | complex | datetime | timedelta
numbers = int | float
strings = str | bytes
TupleType = tuple[strings | numbers]
ListType = list[strings | numbers]
DictType = dict[str, strings | numbers]
datastores = TupleType | ListType | set | DictType

TypeData = (
    list[dict[str, str | Numbers | datetime]] | dict[str, str | Numbers | datetime]
)
binds = numbers | strings | TupleType | ListType | DictType

Numbers = int | float | complex | datetime | timedelta
TypeValues = str | Numbers | list | tuple
SubDict = dict[str, TypeValues | Numbers]
TypeHint = list[str | Numbers | SubDict] | SubDict

DataStores = TypeVar("DataStores", bound=datastores)
AnyType = TypeVar("AnyType", bound=binds)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")
AnyStr = TypeVar("AnyStr", bound=strings)
app_name = Literal["Quart", "Worker"]
StrPath = str | PathLike
ReturnFormataTempo = datetime | float | int | bool | str
TypeLog = Literal["log", "success", "warning", "info", "error"]
StatusType = Literal["Inicializando", "Em Execução", "Finalizado", "Falha"]


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
        return self

    def __repr__(self) -> str:
        return self

    def __instancecheck__(self, instance: T) -> bool:
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


__all__ = ["BotData"]
