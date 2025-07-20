# noqa: D100
from typing import Any, Iterator, Protocol, Self, Type, TypeVar, cast

from jpype import JClass

from java.io import FileInputStream

_TProvider = TypeVar("Provider")
TFileInputStream = Type[FileInputStream]


class KeyStore(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107
    @classmethod
    def getInstance(cls, TypeInstance: str) -> Self: ...  # noqa: N802, N803, D102
    def load(  # noqa: D102
        self,
        FileInputStream: TFileInputStream,  # noqa: N803
        Password: list[str],  # noqa: N803
    ) -> None: ...
    def aliases(self) -> Iterator[str]: ...  # noqa: D102
    def containsAlias(self, alias: str) -> bool: ...  # noqa: N803, N802, D102
    def deleteEntry(self, alias: str) -> None: ...  # noqa: N803, N802, D102
    def entryInstanceOf(self, alias: str, entryClass: type) -> bool: ...  # noqa: N803, N802, D102
    def equals(self, obj: Any) -> bool: ...  # noqa: D102
    def getAttributes(self, alias: str) -> list[Any]: ...  # noqa: N803, N802, D102
    def getCertificate(self, alias: str) -> Any: ...  # noqa: N803, N802, D102
    def getCertificateAlias(self, cert: Any) -> str: ...  # noqa: N803, N802, D102
    def getCertificateChain(self, alias: str) -> list[Any]: ...  # noqa: N803, N802, D102
    def getClass(self) -> type: ...  # noqa: N803, N802, D102
    def getCreationDate(self, alias: str) -> Any: ...  # noqa: N803, N802, D102
    @classmethod
    def getDefaultType(cls) -> str: ...  # noqa: N803, N802, D102
    def getEntry(self, alias: str, protParam: Any) -> Any: ...  # noqa: N803, N802, D102
    def getKey(self, alias: str, password: list[str]) -> Any: ...  # noqa: N803, N802, D102
    def getProvider(self) -> Any: ...  # noqa: N803, N802, D102
    def getType(self) -> str: ...  # noqa: N803, N802, D102
    def hashCode(self) -> int: ...  # noqa: N803, N802, D102


class Signature(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107
    @classmethod
    def getInstance(cls, algorithm: str) -> Self: ...  # noqa: N803, N802, D102
    def initSign(self, privateKey: Any) -> None: ...  # noqa: N803, N802, D102
    def initVerify(self, publicKey: Any) -> None: ...  # noqa: N803, N802, D102
    def update(self, data: bytes) -> None: ...  # noqa: D102
    def sign(self) -> bytes: ...  # noqa: D102
    def verify(self, signature: bytes) -> bool: ...  # noqa:   D102
    def getAlgorithm(self) -> str: ...  # noqa: N803, N802, D102
    def getProvider(self) -> Any: ...  # noqa: N803, N802, D102
    def setParameter(self, param: str, value: Any) -> None: ...  # noqa: N803, N802, D102
    def getParameter(self, param: str) -> Any: ...  # noqa: N803, N802, D102


class Security(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107
    @classmethod
    def addProvider(cls, provider: _TProvider) -> _TProvider: ...  # noqa: N802, D102


Security = cast(Security, JClass("java.security.Security"))
KeyStore = cast(KeyStore, JClass("java.security.KeyStore"))
Signature = cast(Signature, JClass("java.security.Signature"))
