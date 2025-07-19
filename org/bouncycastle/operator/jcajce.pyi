from typing import Protocol

class JcaDigestCalculatorProviderBuilder(Protocol):
    def __init__(self) -> None: ...

class JcaContentSignerBuilder(Protocol):
    def __init__(self) -> None: ...
