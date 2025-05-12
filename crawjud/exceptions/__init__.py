"""Módulo de tratamento de exceptions do robô."""


class BaseCrawJUDError(Exception):
    """Base exception class for CrawJUD-specific errors."""


class DriverNotCreatedError(BaseCrawJUDError):
    """Handler de erro de inicialização do WebDriver."""
