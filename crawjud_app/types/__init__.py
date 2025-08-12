"""Defina tipos e aliases utilizados em toda a aplicação CrawJUD.

Este módulo centraliza definições de tipos, facilitando a tipagem
de dados, parâmetros e retornos em funções e classes do projeto.

"""

from datetime import datetime, timedelta
from os import PathLike
from typing import Literal, TypeVar

from crawjud_app.types.bot import BotData

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


__all__ = ["BotData"]
