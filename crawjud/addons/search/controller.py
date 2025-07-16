"""Módulo controller de pesquisa de processos."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from addons.printlogs import PrintMessage
    from crawjud.addons.interator import Interact
    from crawjud.types.elements import type_elements


class SearchController:
    """Controller class for search operations."""

    typebot: str
    driver: WebDriver
    wait: WebDriverWait
    elements: type[type_elements]
    bot_data: dict[str, str]
    interact: Interact
    prt: PrintMessage

    def __init__(
        self,
        typebot: str,
        driver: WebDriver,
        wait: WebDriverWait,
        elements: type[type_elements],
        bot_data: dict[str, str],
        interact: Interact,
        prt: PrintMessage,
    ) -> None:
        """Inicializador do SearchController."""
        self.typebot = typebot
        self.driver = driver
        self.wait = wait
        self.elements = elements
        self.bot_data = bot_data
        self.interact = interact
        self.prt = prt

    def search(self, bot_data: dict[str, str]) -> bool:  # noqa: D102
        raise NotImplementedError("This method should be implemented by subclasses.")

    def search_proc(self) -> bool:  # noqa: D102
        raise NotImplementedError("This method should be implemented by subclasses.")

    def search_proc_parte(self) -> bool:  # noqa: D102
        raise NotImplementedError("This method should be implemented by subclasses.")
