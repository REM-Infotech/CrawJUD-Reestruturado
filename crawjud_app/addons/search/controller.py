"""Módulo pesquisa de processos."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from crawjud_app.abstract._master import AbstractCrawJUD

if TYPE_CHECKING:
    from httpx import Client

    from interface.dict.bot import BotData
    from interface.types.pje import DictResults


class SearchController[T](AbstractCrawJUD):
    """Controller class for search operations."""

    def __init_subclass__(cls) -> None:  # noqa: D105
        if not hasattr(cls, "search"):
            msg = f"Subclasses of {cls.__name__} must implement the 'search' method."
            raise NotImplementedError(msg)

        cls.subclasses_search[cls.__name__.lower()] = cls

    @abstractmethod
    def search(self, *args: T, **kwargs: T) -> T:
        """Realize a busca de processos conforme os parâmetros fornecidos.

        Args:
            *args (T): Argumentos posicionais para a busca.
            **kwargs (T): Argumentos nomeados para a busca.

        Returns:
            T: Resultado da busca conforme o tipo definido.

        Raises:
            NotImplementedError: Caso o método não seja implementado pela subclasse.

        """

    @abstractmethod
    def desafio_captcha(  # noqa: D102
        self,
        row: int,
        data: BotData,
        id_processo: str,
        client: Client,
    ) -> DictResults:
        return NotImplementedError("Função não implementada!")
