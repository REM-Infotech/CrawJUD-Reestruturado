from typing import Protocol

class BouncyCastleProvider(Protocol):
    def __init__(self) -> None: ...
