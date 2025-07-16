"""Módulo controller de autenticação."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from addons.printlogs import PrintMessage
    from crawjud.types.elements import type_elements


class AuthController:  # noqa: B903
    """Controller class for authentication operations."""

    username: str
    password: str
    system: str
    driver: WebDriver
    wait: WebDriverWait
    elements: type_elements
    prt: PrintMessage
    subclasses = {}

    def __init__(
        self,
        username: str,
        password: str,
        system: str,
        driver: WebDriver,
        wait: WebDriverWait,
        elements: type_elements,
        prt: PrintMessage,
    ) -> None:
        """Inicializador do AuthController."""
        self.username = username
        self.password = password
        self.system = system
        self.driver = driver
        self.wait = wait
        self.elements = elements
        self.prt = prt

    @classmethod
    def construct(cls, system: str, *args, **kwargs) -> Self:  # noqa: ANN002, ANN003
        """Método construtor para instanciar a classe."""
        return cls.subclasses.get(system.lower())(*args, **kwargs)

    def __init_subclass__(cls) -> None:  # noqa: D105
        if not hasattr(cls, "auth"):
            raise NotImplementedError(
                f"Subclasses of {cls.__name__} must implement the 'auth' method."
            )

        cls.subclasses[cls.__name__.lower()] = cls

    def auth(self) -> bool:  # noqa: D102
        """Authenticate on system using certificate or credentials.

        Returns:
            bool: True if authentication is successful; False otherwise.

        Waits for page elements, selects certificate if needed, and verifies login.

        """
        raise NotImplementedError("Method 'auth' must be implemented in subclasses.")

    def accept_cert(self, accepted_dir: str) -> None:  # noqa: D102
        """Accept a certificate if required."""
        raise NotImplementedError(
            "Method 'accept_cert' must be implemented in subclasses."
        )
