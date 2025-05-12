"""Módulo controller de autenticação."""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

from crawjud.addons.elements.caixa import CAIXA_AM
from crawjud.addons.elements.calculadoras import TJDFT
from crawjud.addons.elements.elaw import ELAW_AME
from crawjud.addons.elements.esaj import ESAJ_AM
from crawjud.addons.elements.pje import PJE_AM
from crawjud.addons.elements.projudi import PROJUDI_AM

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    type_elements = Union[ESAJ_AM, PROJUDI_AM, ELAW_AME, CAIXA_AM, PJE_AM, TJDFT]


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
