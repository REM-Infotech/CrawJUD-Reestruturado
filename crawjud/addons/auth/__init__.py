"""Módulo de autenticação CrawJUD."""

from __future__ import annotations

from typing import TYPE_CHECKING

from crawjud.addons.auth.elaw import ElawAuth
from crawjud.addons.auth.esaj import EsajAuth
from crawjud.addons.auth.pje import PjeAuth
from crawjud.addons.auth.projudi import ProjudiAuth

if TYPE_CHECKING:
    from crawjud.addons.auth.controller import AuthController

auth_systems: type[AuthController] = {
    "pje": PjeAuth,
    "esaj": EsajAuth,
    "elaw": ElawAuth,
    "projudi": ProjudiAuth,
}


def authenticator(system: str) -> type[AuthController]:
    """Retorna o objeto do autenticador."""
    auth: type[AuthController] = auth_systems[system]

    return auth
