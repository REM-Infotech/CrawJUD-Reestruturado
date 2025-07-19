from typing import Protocol

from java.io import File
from org.bouncycastle.asn1 import ASN1ObjectIdentifier

class CMSSignedDataGenerator(Protocol):
    def __init__(self) -> None: ...

class CMSProcessableByteArray(Protocol):
    def __init__(self) -> None: ...

class CMSProcessableFile(Protocol):
    def __init__(self, *args: ASN1ObjectIdentifier | File | int) -> None: ...
    @staticmethod
    def __doc__() -> str:  # noqa: PYI048
        """
        Java class 'org.bouncycastle.cms.CMSProcessableFile'.

        Extends:
            java.lang.Object
        Interfaces:
            org.bouncycastle.cms.CMSTypedData,
            org.bouncycastle.cms.CMSReadable
        Constructors:
            * CMSProcessableFile(java.io.File)
            * CMSProcessableFile(org.bouncycastle.asn1.ASN1ObjectIdentifier, java.io.File, int)
            * CMSProcessableFile(java.io.File, int)
        """  # noqa: PYI021
        ...
