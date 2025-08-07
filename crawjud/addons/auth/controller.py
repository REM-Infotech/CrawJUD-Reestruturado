"""Módulo controller de autenticação."""

from __future__ import annotations

from abc import abstractmethod

from crawjud.abstract._master import AbstractClassBot


class AuthController[T](AbstractClassBot):  # noqa: B903
    """Controller class for authentication operations."""

    @abstractmethod
    def auth(self, *args: T, **kwargs: T) -> None: ...  # noqa: D102

    def __init_subclass__(cls) -> None:  # noqa: D105
        cls.subclasses_auth[cls.__name__.lower()] = cls
