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


class BotNotFoundError(AttributeError):
    """Exceção para indicar que o robô especificado não foi encontrado.

    Args:
        message (str): Mensagem de erro.

    Returns:
        None

    Raises:
        AttributeError: Sempre que o robô não for localizado.

    """

    def __init__(
        self,
        message: str,
        name: str | None = None,
        obj: object | None = None,
    ) -> None:
        """Inicializa a exceção BotNotFoundError.

        Args:
            message (str): Mensagem de erro.
            name (str | None): Nome do robô, se disponível.
            obj (object | None): Objeto relacionado ao erro, se disponível.



        """
        self.name = name
        self.obj = obj
        super().__init__(message)
