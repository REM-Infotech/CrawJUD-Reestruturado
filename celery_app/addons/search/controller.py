"""Módulo pesquisa de processos."""

from __future__ import annotations

from abc import abstractmethod

from crawjud.types.pje import DictResults
from httpx import Client

from celery_app.abstract._master import AbstractClassBot
from celery_app.types.bot import BotData


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
