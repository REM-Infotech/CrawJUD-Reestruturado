"""Módulo de autenticação CrawJUD."""

from typing import Type, Union

from crawjud.addons.auth.elaw import ElawAuth
from crawjud.addons.auth.esaj import EsajAuth
from crawjud.addons.auth.pje import PjeAuth
from crawjud.addons.auth.projudi import ProjudiAuth

auth_systems = {
    "pje": PjeAuth,
    "esaj": EsajAuth,
    "elaw": ElawAuth,
    "projudi": ProjudiAuth,
}

auth_types = Union[Type[PjeAuth], Type[EsajAuth], Type[ElawAuth], Type[ProjudiAuth]]


def authenticator(system: str) -> auth_types:
    """Retorna o objeto do autenticador."""
    auth: auth_types = auth_systems[system]

    return auth
