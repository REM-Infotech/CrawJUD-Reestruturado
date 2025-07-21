from typing import Protocol, Self

class Certificate(Protocol):
    @classmethod
    def getInstance(cls, enconded_data: bytearray) -> Self: ...  # noqa: N802
    def __init__(self) -> None: ...
