# noqa: D100
from __future__ import annotations

from typing import TypedDict


class SessionDict(TypedDict):  # noqa: D101
    accessed: bool

    modified: bool

    new: bool

    permanent: bool

    sid: str
    _permanent: bool

    license_object: LicenseUserDict


class LicenseUserDict(TypedDict):  # noqa: D101
    id: int
    name_client: str
    cpf_cnpj: str
    license_token: str
