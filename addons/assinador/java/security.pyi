from typing import Any, Iterator, Protocol, Self

from java.io import FileInputStream

class KeyStore(Protocol):
    def __init__(self) -> None: ...
    @classmethod
    def getInstance(cls, TypeInstance: str) -> Self: ...  # noqa: N802, N803
    def load(self, FileInputStream: FileInputStream, Password: list[str]) -> None: ...  # noqa:  N803
    def aliases(self) -> Iterator[str]: ...
    def containsAlias(self, alias: str) -> bool: ...  # noqa: N803, N802
    def deleteEntry(self, alias: str) -> None: ...  # noqa: N803, N802
    def entryInstanceOf(self, alias: str, entryClass: type) -> bool: ...  # noqa: N803, N802
    def equals(self, obj: Any) -> bool: ...
    def getAttributes(self, alias: str) -> list[Any]: ...  # noqa: N803, N802
    def getCertificate(self, alias: str) -> Any: ...  # noqa: N803, N802
    def getCertificateAlias(self, cert: Any) -> str: ...  # noqa: N803, N802
    def getCertificateChain(self, alias: str) -> list[Any]: ...  # noqa: N803, N802
    def getClass(self) -> type: ...  # noqa: N803, N802
    def getCreationDate(self, alias: str) -> Any: ...  # noqa: N803, N802
    @classmethod
    def getDefaultType(cls) -> str: ...  # noqa: N803, N802
    def getEntry(self, alias: str, protParam: Any) -> Any: ...  # noqa: N803, N802
    def getKey(self, alias: str, password: list[str]) -> Any: ...  # noqa: N803, N802
    def getProvider(self) -> Any: ...  # noqa: N803, N802
    def getType(self) -> str: ...  # noqa: N803, N802
    def hashCode(self) -> int: ...  # noqa: N803, N802

class Signature(Protocol):
    def __init__(self) -> None: ...
    @classmethod
    def getInstance(cls, algorithm: str) -> Self: ...  # noqa: N803, N802
    def initSign(self, privateKey: Any) -> None: ...  # noqa: N803, N802
    def initVerify(self, publicKey: Any) -> None: ...  # noqa: N803, N802
    def update(self, data: bytes) -> None: ...
    def sign(self) -> bytes: ...
    def verify(self, signature: bytes) -> bool: ...
    def getAlgorithm(self) -> str: ...  # noqa: N803, N802
    def getProvider(self) -> Any: ...  # noqa: N803, N802
    def setParameter(self, param: str, value: Any) -> None: ...  # noqa: N803, N802
    def getParameter(self, param: str) -> Any: ...  # noqa: N803, N802
