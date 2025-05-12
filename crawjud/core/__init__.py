"""Módulo núcleo de controle dos robôs."""

from time import perf_counter


class CrawJUD:
    """CrawJUD bot core class.

    Manages the initialization, setup, and authentication processes
    of the CrawJUD bot.
    """

    bot_data: dict[str, str]
    start_time: float

    def __init__(self, *args: str, **kwargs: str) -> None:
        """Inicializador do núcleo."""
        self.start_time = perf_counter()
