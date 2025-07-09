# noqa: D100
from typing import TypedDict


class CredendialDictSelect(TypedDict):  # noqa: D101
    value: int
    text: str


class CredendialsSystemDict(TypedDict):  # noqa: D101
    elaw: list[CredendialDictSelect]
    projudi: list[CredendialDictSelect]
    esaj: list[CredendialDictSelect]
    pje: list[CredendialDictSelect]


class CredendialsDict(TypedDict):  # noqa: D101
    id: int
    nome_credencial: str
    system: str
    login_method: str
