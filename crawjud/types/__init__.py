"""Web types module."""

from datetime import datetime, timedelta
from os import PathLike
from typing import Dict, List, Literal, Tuple, TypeVar, Union

from crawjud.types.bot import BotData

T = TypeVar("T", bound=BotData)
Numbers = Union[int, float, complex, datetime, timedelta]
numbers = Union[int, float]
strings = Union[str, bytes]
TupleType = Tuple[Union[strings, numbers]]
ListType = List[Union[strings, numbers]]
DictType = Dict[str, Union[strings, numbers]]
datastores = Union[
    TupleType,
    ListType,
    set,
    DictType,
]

TypeData = Union[
    list[dict[str, Union[str, Numbers, datetime]]],
    dict[str, Union[str, Numbers, datetime]],
]
binds = Union[
    numbers,
    strings,
    TupleType,
    ListType,
    DictType,
]

Numbers = Union[int, float, complex, datetime, timedelta]
TypeValues = Union[str, Numbers, list, tuple]
SubDict = dict[str, Union[TypeValues, Numbers]]
TypeHint = Union[list[str | Numbers | SubDict] | SubDict]

DataStores = TypeVar("DataStores", bound=datastores)
AnyType = TypeVar("AnyType", bound=binds)
WrappedFnReturnT = TypeVar("WrappedFnReturnT")
AnyStr = TypeVar("AnyStr", bound=strings)
app_name = Literal["Quart", "Worker"]
StrPath = Union[str, PathLike]
ReturnFormataTempo = Union[datetime, float, int, bool, str]
TypeLog = Literal["log", "success", "warning", "info", "error"]
StatusType = Literal["Inicializando", "Em Execução", "Finalizado", "Falha"]


__all__ = ["BotData"]
