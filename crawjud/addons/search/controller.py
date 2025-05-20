"""Módulo controller de pesquisa de processos."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from crawjud.types.elements import type_elements


class SearchController:
    """Controller class for search operations."""

    typebot: str
    driver: WebDriver
    wait: WebDriverWait
    elements: type_elements

    def __init__(
        self,
        typebot: str,
        driver: WebDriver,
        wait: WebDriverWait,
        elements: type_elements,
    ) -> None:
        """Inicializador do SearchController."""
        self.typebot = typebot
        self.driver = driver
        self.wait = wait
        self.elements = type_elements
