from pathlib import Path
from typing import Any, Protocol

class Object(Protocol):
    def equals(self, obj: Any) -> bool: ...
    def getClass(self) -> type: ...  # noqa: N802
    def hashCode(self) -> int: ...  # noqa: N802
    def notify(self) -> None: ...
    def notifyAll(self) -> None: ...  # noqa: N802
    def toString(self) -> str: ...  # noqa: N802
    def wait(self, timeout: float = ...) -> None: ...

class URI(Protocol):
    def __init__(self, *args: str | int | Path) -> None: ...
