"""Módulo de pesquisa CrawJUD."""

from __future__ import annotations

from typing import Union

from crawjud.addons.search.elaw import ElawSearch
from crawjud.addons.search.esaj import EsajSearch
from crawjud.addons.search.projudi import ProjudiSearch

search_types = Union[ElawSearch, EsajSearch, ProjudiSearch]
search_systems = {
    "elaw": ElawSearch,
    "esaj": EsajSearch,
    "projudi": ProjudiSearch,
}


def search_engine(system: str) -> search_types:
    """Retorna o objeto do autenticador."""
    search: search_types = search_systems[system]

    return search
