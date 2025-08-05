# noqa: D100
from typing import Protocol, cast

from jpype import JClass


class AttributeTable(Protocol): ...  # noqa: D101


AttributeTable = cast(
    AttributeTable, JClass("org.bouncycastle.asn1.cms.AttributeTable")
)
