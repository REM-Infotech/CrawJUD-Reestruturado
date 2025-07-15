# noqa: D100
from __future__ import annotations

from typing import TypedDict


class CurrentUser(TypedDict):  # noqa: D101
    id: int
    login: str
    nome_usuario: str
    email: str


class LicenseUserDict(TypedDict):  # noqa: D101
    id: int
    name_client: str
    cpf_cnpj: str
    license_token: str


class SessionDict(TypedDict):  # noqa: D101
    accessed: bool
    modified: bool
    new: bool
    permanent: bool
    sid: str
    _permanent: bool
    current_user: CurrentUser
    license_object: LicenseUserDict
