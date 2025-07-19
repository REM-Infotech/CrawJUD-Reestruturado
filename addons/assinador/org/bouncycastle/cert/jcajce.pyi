from typing import Protocol

class JcaCertStore(Protocol):
    def __init__(self) -> None: ...

class JcaX509CertificateHolder(Protocol):
    def __init__(self) -> None: ...
