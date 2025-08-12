"""Módulo de tratamento de exceptions do robô."""


class BaseCrawJUDError(Exception):
    """Base exception class for CrawJUD-specific errors."""


class DriverNotCreatedError(BaseCrawJUDError):
    """Handler de erro de inicialização do WebDriver."""


class AuthenticationError(BaseCrawJUDError):
    """Handler de erro de autenticação."""

    def __init__(self, message: str = "Erro de autenticação.") -> None:
        """Inicializa a mensagem de erro."""
        super().__init__(message)


class BaseExceptionCeleryAppError(Exception):
    """Base exception class for Celery app errors."""
