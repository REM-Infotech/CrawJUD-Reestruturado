"""Web types module."""

from datetime import datetime, timedelta
from typing import Dict, List, Literal, Tuple, TypeVar, Union

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
