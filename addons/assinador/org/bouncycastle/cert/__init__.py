# noqa: D104

from typing import Protocol, cast

from jpype import JClass


class X509CertificateHolder(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


X509CertificateHolder = cast(
    X509CertificateHolder,
    JClass("org.bouncycastle.cert.X509CertificateHolder"),
)
