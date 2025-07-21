# noqa: D100
from typing import Protocol, cast

from jpype import JClass


class JcaCertStore(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


class JcaX509CertificateHolder(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


JcaCertStore = cast(JcaCertStore, JClass("org.bouncycastle.cert.jcajce.JcaCertStore"))
JcaX509CertificateHolder = cast(
    JcaX509CertificateHolder,
    JClass("org.bouncycastle.cert.jcajce.JcaX509CertificateHolder"),
)
