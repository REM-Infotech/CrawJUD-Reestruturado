"""
Implemente integrações com classes Java do pacote org.bouncycastle.cms.

Este módulo fornece tipos e integrações para uso com JPype e o pacote BouncyCastle.

"""

from typing import Protocol, cast

from jpype import JClass

from addons.assinador.java.io import File
from addons.assinador.org.bouncycastle.asn1 import ASN1ObjectIdentifier


class CMSSignedData(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107
    def getEncoded(self) -> bytes: ...  # noqa: N802, D102


class CMSSignedDataGenerator(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


class CMSProcessableByteArray(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


class CMSProcessableFile:  # noqa: D101
    def __init__(self, *args: ASN1ObjectIdentifier | File | int) -> None: ...  # noqa: D107


from org.bouncycastle import cms  # noqa: E402, F403

CMSProcessableFile = cast(
    CMSProcessableFile, JClass("org.bouncycastle.cms.CMSProcessableFile")
)
CMSSignedDataGenerator = cast(CMSSignedDataGenerator, cms.CMSSignedDataGenerator)
CMSProcessableByteArray = cast(
    CMSProcessableByteArray, JClass("org.bouncycastle.cms.CMSProcessableByteArray")
)
CMSSignedData = cast(CMSSignedData, JClass("org.bouncycastle.cms.CMSSignedData"))
