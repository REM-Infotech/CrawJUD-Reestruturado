# noqa: D100
from typing import Protocol, cast

from jpype import JClass


class JcaSignerInfoGeneratorBuilder(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


class JcaSimpleSignerInfoGeneratorBuilder(Protocol): ...  # noqa: D101


JcaSimpleSignerInfoGeneratorBuilder = cast(
    JcaSimpleSignerInfoGeneratorBuilder,
    JClass("org.bouncycastle.cms.jcajce.JcaSimpleSignerInfoGeneratorBuilder"),
)

JcaSignerInfoGeneratorBuilder = cast(
    JcaSignerInfoGeneratorBuilder,
    JClass("org.bouncycastle.cms.jcajce.JcaSignerInfoGeneratorBuilder"),
)
