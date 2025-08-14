"""Defina tipos e aliases utilizados em toda a aplicação CrawJUD.

Este módulo centraliza definições de tipos, facilitando a tipagem
de dados, parâmetros e retornos em funções e classes do projeto.

"""

from datetime import datetime, timedelta
from os import PathLike

from interface.dict.bot import BotData

# Tipos de retorno das funções


# Tipos primitivos do Python
type PyNumbers = int | float | complex | datetime | timedelta
type PyStrings = str | bytes

# Tipos de tuplas, listas e dicionários
type TupleType = tuple[PyStrings | PyNumbers]
type ListType = list[PyStrings | PyNumbers]
type DictType = dict[str, PyStrings | PyNumbers]

# Tipo de armazenamento de dados
type DataStores = TupleType | ListType | set | DictType
type Binds = PyNumbers | PyStrings | TupleType | ListType | DictType

# Definição do tipo "StrPath"
type StrPath = str | PathLike
type ReturnFormataTempo = datetime | float | int | bool | str


__all__ = ["BotData"]
