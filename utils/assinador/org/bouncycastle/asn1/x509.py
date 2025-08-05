# noqa: D100
from typing import Protocol, Self, cast

from jpype import JClass


class Certificate(Protocol):  # noqa: D101
    @classmethod
    def getInstance(cls, enconded_data: bytearray) -> Self: ...  # noqa: D102, N802
    def __init__(self) -> None: ...  # noqa: D107


Certificate = cast(Certificate, JClass("org.bouncycastle.asn1.x509.Certificate"))
