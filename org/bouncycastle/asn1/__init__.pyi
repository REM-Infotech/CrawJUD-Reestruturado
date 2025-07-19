from typing import Protocol, Self

class ASN1Primitive(Protocol):
    def __init__(self) -> None: ...
    @classmethod
    def fromByteArray(cls, byte_array: bytearray) -> Self: ...  # noqa: N802

class ASN1ObjectIdentifier(Protocol): ...
