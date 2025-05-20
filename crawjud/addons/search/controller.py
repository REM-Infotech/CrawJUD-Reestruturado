"""Módulo controller de pesquisa de processos."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from crawjud.addons.interator import Interact
    from crawjud.types.elements import type_elements

    elements_type = TypeVar("ElementsType", bound=type_elements)


class SearchController:
    """Controller class for search operations."""

    typebot: str
    driver: WebDriver
    wait: WebDriverWait
    elements: elements_type
    bot_data: dict[str, str]
    interact: Interact

    def __init__(
        self,
        typebot: str,
        driver: WebDriver,
        wait: WebDriverWait,
        elements: elements_type,
        bot_data: dict[str, str],
        interact: Interact,
    ) -> None:
        """Inicializador do SearchController."""
        self.typebot = typebot
        self.driver = driver
        self.wait = wait
        self.elements = elements
        self.bot_data = bot_data
        self.interact = interact
