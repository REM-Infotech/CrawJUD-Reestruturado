"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING

from crawjud.addons.auth import authenticator
from crawjud.addons.elements import ElementsBot
from crawjud.addons.search import SearchBot
from crawjud.addons.webdriver import DriverBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver

    from crawjud.types.elements import type_elements


class CrawJUD:
    """CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    bot_data: dict[str, str]
    start_time: float
    driver: WebDriver
    search: SearchBot
    senhatoken: str
    elements: type_elements

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo."""
        self.start_time = perf_counter()

        for k, v in list(kwargs.items()):
            setattr(self, k, v)

        # Instancia o WebDriver
        driverbot = DriverBot(kwargs.get("preferred_browser", "chrome"))()
        self.driver = driverbot[0]
        self.wait = driverbot[1]

        self.elements = ElementsBot().config().bot_elements

        # Autenticação com os sistemas
        auth = authenticator(kwargs.get("system"))(
            username=kwargs.get("username"),
            password=kwargs.get("password"),
            driver=self.driver,
            wait=self.wait,
        )
        auth.auth()

        # self.search = SearchBot.setup()
