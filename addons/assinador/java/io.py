# noqa: D100
from typing import Protocol, Self, cast

from jpype import JClass


class File(Protocol):  # noqa: D101
    def __init__(self, *args: str | type[Self]) -> None: ...  # noqa: D107


class FileDescriptor(Protocol):  # noqa: D101
    def __init__(self, *args: str | type[Self]) -> None: ...  # noqa: D107


class FileChannel(Protocol):  # noqa: D101
    def __init__(self, *args: str | type[Self]) -> None: ...  # noqa: D107


class Provider(Protocol):  # noqa: D101
    def __init__(self, *args: str | type[Self]) -> None: ...  # noqa: D107


class FileInputStream(Protocol):  # noqa: D101
    @classmethod
    def nullInputStream(cls) -> Self: ...  # noqa: N802, D102
    def available(self) -> int: ...  # noqa: D102
    def close(self) -> None: ...  # noqa: D102
    def getChannel(self) -> FileChannel: ...  # noqa: N802, D102
    def getFD(self) -> FileDescriptor: ...  # noqa: N802, D102
    def mark(self, readlimit: int) -> None: ...  # noqa: D102
    def markSupported(self) -> bool: ...  # noqa: N802, D102
    def read(self, *args, **kwargs) -> int: ...  # noqa: ANN003, N802, ANN002, D102
    def readAllBytes(self) -> bytes: ...  # noqa: N802, D102
    def readNBytes(self, Len: int) -> bytes: ...  # noqa: N802, N803, D102
    def reset(self) -> None: ...  # noqa: D102
    def skip(self, n: int) -> int: ...  # noqa: D102
    def skipNBytes(self, n: int) -> None: ...  # noqa: N802, D102


FileInputStream = cast(FileInputStream, JClass("java.io.FileInputStream"))
File = cast(File, JClass("java.io.File"))
FileDescriptor = cast(FileDescriptor, JClass("java.io.FileDescriptor"))
FileChannel = cast(FileChannel, JClass("java.nio.channels.FileChannel"))
Provider = cast(Provider, JClass("java.security.Provider"))
