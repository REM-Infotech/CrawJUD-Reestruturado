"""Módulo controller de autenticação."""

from __future__ import annotations

from abc import abstractmethod

from crawjud_app.abstract._master import AbstractCrawJUD


class AuthController[T](AbstractCrawJUD):
    """Controller class for authentication operations."""

    @abstractmethod
    def auth(self, *args: T, **kwargs: T) -> None: ...  # noqa: D102

    def __init_subclass__(cls) -> None:  # noqa: D105
        cls.subclasses_auth[cls.__name__.lower()] = cls
