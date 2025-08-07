"""Módulo pesquisa de processos."""

from __future__ import annotations

from abc import abstractmethod

from httpx import Client

from crawjud.abstract._master import AbstractClassBot
from crawjud.types.bot import BotData
from crawjud.types.pje import DictResults


class SearchController[T](AbstractClassBot):
    """Controller class for search operations."""

    def __init_subclass__(cls) -> None:  # noqa: D105
        if not hasattr(cls, "search"):
            raise NotImplementedError(
                f"Subclasses of {cls.__name__} must implement the 'search' method."
            )

        cls.subclasses_search[cls.__name__.lower()] = cls

    @abstractmethod
    def search(self, *args: T, **kwargs: T) -> T: ...  # noqa: D102

    def desafio_captcha(  # noqa: D102
        self,
        row: int,
        data: BotData,
        id_processo: str,
        client: Client,
    ) -> DictResults:
        return NotImplementedError("Função não implementada!")
