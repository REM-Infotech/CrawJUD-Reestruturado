# noqa: D100
from typing import Protocol, cast

from jpype import JClass


class BouncyCastleProvider(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


BouncyCastleProvider = cast(
    BouncyCastleProvider,
    JClass("org.bouncycastle.jce.provider.BouncyCastleProvider"),
)
