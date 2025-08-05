# noqa: D100
from typing import Any, Protocol, cast

from jpype import JClass

from utils.assinador.java.lang import Object


class JcaDigestCalculatorProviderBuilder(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107


class JcaContentSignerBuilder(Protocol):  # noqa: D101
    def __init__(self) -> None: ...  # noqa: D107
    def build(self, *args: Any, **kwargs: Any) -> Object: ...  # noqa: D102


JcaContentSignerBuilder = cast(
    JcaContentSignerBuilder,
    JClass("org.bouncycastle.operator.jcajce.JcaContentSignerBuilder"),
)

JcaDigestCalculatorProviderBuilder = cast(
    JcaDigestCalculatorProviderBuilder,
    JClass("org.bouncycastle.operator.jcajce.JcaDigestCalculatorProviderBuilder"),
)
