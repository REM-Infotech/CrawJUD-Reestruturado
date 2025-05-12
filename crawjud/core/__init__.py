"""Módulo núcleo de controle dos robôs."""

from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING

from crawjud.addons.search import SearchBot
from crawjud.addons.webdriver import DriverBot

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver


class CrawJUD:
    """CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    bot_data: dict[str, str]
    start_time: float
    driver: WebDriver
    search: SearchBot

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo."""
        self.start_time = perf_counter()
        driverbot = DriverBot(kwargs.get("preferred_browser", "chrome"))()
        self.driver = driverbot[0]
        self.wait = driverbot[1]

        # self.search = SearchBot.setup()
