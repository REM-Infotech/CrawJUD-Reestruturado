from typing import Any, Protocol

from java.lang import Object

class JcaDigestCalculatorProviderBuilder(Protocol):
    def __init__(self) -> None: ...

class JcaContentSignerBuilder(Protocol):
    def __init__(self) -> None: ...
    def build(self, *args: Any, **kwargs: Any) -> Object: ...
