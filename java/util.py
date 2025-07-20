# noqa: D100
from __future__ import annotations

from typing import Any, Iterator, Protocol, Type, cast

from jpype import JClass


class ArrayList(Protocol):  # noqa: D101
    def __init__(self, initial: list[Any] = ...) -> None: ...  # noqa: D107
    def add(self, element: Any) -> bool: ...  # noqa: D102
    def addAll(self, collection: list[Any]) -> bool: ...  # noqa: N802, D102
    def clear(self) -> None: ...  # noqa: D102
    def contains(self, element: Any) -> bool: ...  # noqa: D102
    def get(self, index: int) -> Any: ...  # noqa: D102
    def indexOf(self, element: Any) -> int: ...  # noqa: N802, D102
    def isEmpty(self) -> bool: ...  # noqa: N802, D102
    def iterator(self) -> Iterator[Any]: ...  # noqa: D102
    def remove(self, element: Any) -> bool: ...  # noqa: D102
    def removeAt(self, index: int) -> Any: ...  # noqa: N802, D102
    def size(self) -> int: ...  # noqa: D102
    def toArray(self) -> list[Any]: ...  # noqa: N802, D102
    def set(self, index: int, element: Any) -> Any: ...  # noqa: D102
    def subList(self, fromIndex: int, toIndex: int) -> Type[ArrayList]: ...  # noqa: N802, N803, D102


ArrayList = cast(ArrayList, JClass("java.util.ArrayList"))
