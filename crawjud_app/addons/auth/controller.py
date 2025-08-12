"""Módulo controller de autenticação."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from crawjud_app.abstract._master import AbstractClassBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class AuthController[T](AbstractClassBot):
    """Controller class for authentication operations."""

    driver: WebDriver

    @abstractmethod
    def auth(self, *args: T, **kwargs: T) -> None: ...  # noqa: D102

    def __init_subclass__(cls) -> None:  # noqa: D105
        cls.subclasses_auth[cls.__name__.lower()] = cls

    def formata_url_pje(  # noqa: D102
        self,
        _format: str = "login",
        *args: T,
        **kwargs: T,
    ) -> str:
        formats = {
            "login": f"https://pje.trt{self.regiao}.jus.br/primeirograu/login.seam",
            "validate_login": f"https://pje.trt{self.regiao}.jus.br/pjekz/",
            "search": f"https://pje.trt{self.regiao}.jus.br/consultaprocessual/",
        }

        return formats[_format]
