# noqa: D104
from pathlib import Path
from typing import Any, Protocol, cast

from jpype import JClass


class Object(Protocol):  # noqa: D101
    def equals(self, obj: Any) -> bool: ...  # noqa: D102
    def getClass(self) -> type: ...  # noqa: N802,D102
    def hashCode(self) -> int: ...  # noqa: N802,D102
    def notify(self) -> None: ...  # noqa: D102
    def notifyAll(self) -> None: ...  # noqa: N802,D102
    def toString(self) -> str: ...  # noqa: N802,D102
    def wait(self, timeout: float = ...) -> None: ...  # noqa: D102


class URI(Protocol):  # noqa: D101
    def __init__(self, *args: str | int | Path) -> None: ...  # noqa: D107


URI = cast(URI, JClass("java.net.URI"))
Object = cast(Object, JClass("java.lang.Object"))
