from typing import Protocol

class JcaSignerInfoGeneratorBuilder(Protocol):
    def __init__(self) -> None: ...

class JcaContentSignerBuilder(Protocol):
    def __init__(self) -> None: ...
