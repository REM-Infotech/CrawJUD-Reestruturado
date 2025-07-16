"""Módulo de pesquisa CrawJUD."""

from __future__ import annotations

from typing import TYPE_CHECKING

from crawjud.addons.search.elaw import ElawSearch
from crawjud.addons.search.esaj import EsajSearch
from crawjud.addons.search.projudi import ProjudiSearch

if TYPE_CHECKING:
    from crawjud.addons.search.controller import SearchController

search_systems: dict[str, type[SearchController]] = {
    "elaw": ElawSearch,
    "esaj": EsajSearch,
    "projudi": ProjudiSearch,
}


def search_engine(system: str) -> type[SearchController]:
    """Retorna o objeto do autenticador."""
    search: type[SearchController] = search_systems[system]

    return search
