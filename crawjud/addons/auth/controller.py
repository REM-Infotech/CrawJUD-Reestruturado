"""Módulo controller de autenticação."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from crawjud.types.elements import type_elements


class AuthController:  # noqa: B903
    """Controller class for authentication operations."""

    username: str
    password: str
    system: str
    driver: WebDriver
    wait: WebDriverWait
    elements: type_elements

    def __init__(
        self,
        username: str,
        password: str,
        system: str,
        driver: WebDriver,
        wait: WebDriverWait,
        elements: type_elements,
    ) -> None:
        """Inicializador do AuthController."""
        self.username = username
        self.password = password
        self.system = system
        self.driver = driver
        self.wait = wait
        self.elements = elements
