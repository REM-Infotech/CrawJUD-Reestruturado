from typing import Protocol

class CMSSignedDataGenerator(Protocol):
    def __init__(self) -> None: ...

class CMSProcessableByteArray(Protocol):
    def __init__(self) -> None: ...
