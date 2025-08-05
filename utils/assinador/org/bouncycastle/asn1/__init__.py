# noqa: D104
from typing import Protocol, Self, cast

from jpype import JClass


class ASN1Primitive(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107
    @classmethod
    def fromByteArray(cls, byte_array: bytearray) -> Self: ...  # noqa: D102, N802


class ASN1ObjectIdentifier(Protocol): ...  # noqa: D101


class ASN1Encoding(Protocol):  # noqa: D101
    DER: str = "DER"
    DL: str = "DL"
    BER: str = "BER"


ASN1ObjectIdentifier = cast(
    ASN1ObjectIdentifier, JClass("org.bouncycastle.asn1.ASN1ObjectIdentifier")
)

ASN1Primitive = cast(ASN1Primitive, JClass("org.bouncycastle.asn1.ASN1Primitive"))
ASN1Encoding = cast(ASN1Encoding, JClass("org.bouncycastle.asn1.ASN1Encoding"))
