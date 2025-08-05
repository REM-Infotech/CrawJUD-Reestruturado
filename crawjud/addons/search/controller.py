"""Módulo pesquisa de processos."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.wait import WebDriverWait

    from crawjud.types import BotData
    from crawjud.types.elements import type_elements
    from utils.printlogs import PrintMessage


class SearchController:
    """Controller class for search operations."""

    typebot: str
    driver: WebDriver
    wait: WebDriverWait
    elements: type[type_elements]
    bot_data: BotData
    prt: PrintMessage

    subclasses = {}

    def __init__(
        self,
        typebot: str,
        driver: WebDriver,
        wait: WebDriverWait,
        elements: type[type_elements],
        bot_data: dict[str, str],
        prt: PrintMessage,
    ) -> None:
        """Inicializador do SearchController."""
        self.typebot = typebot
        self.driver = driver
        self.wait = wait
        self.elements = elements
        self.bot_data = bot_data
        self.prt = prt

    @classmethod
    def construct(cls, system: str, *args, **kwargs) -> Self:  # noqa: ANN002, ANN003
        """Método construtor para instanciar a classe."""
        return cls.subclasses.get(system.lower())(*args, **kwargs)

    def __init_subclass__(cls) -> None:  # noqa: D105
        if not hasattr(cls, "search"):
            raise NotImplementedError(
                f"Subclasses of {cls.__name__} must implement the 'search' method."
            )

        cls.subclasses[cls.__name__.replace("Search", "").lower()] = cls

    def search(self, bot_data: dict[str, str]) -> bool:  # noqa: D102
        raise NotImplementedError("This method should be implemented by subclasses.")

    def search_proc(self) -> bool:  # noqa: D102
        raise NotImplementedError("This method should be implemented by subclasses.")

    def search_proc_parte(self) -> bool:  # noqa: D102
        raise NotImplementedError("This method should be implemented by subclasses.")
