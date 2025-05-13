"""Módulo de controle de exceptions dos bots."""

import traceback

from crawjud.exceptions import BaseCrawJUDError


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""

    def __init__(self, exception: Exception, bot_execution_id: str = None) -> None:
        """Inicializador da instância de exceção."""
        message = "\n".join(traceback.format_exception(exception))
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class ExecutionError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(self, exception: Exception, bot_execution_id: str = None) -> None:
        """Inicializador da instância de exceção."""
        message = "\n".join(traceback.format_exception(exception))
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class LoginSystemError(BaseCrawJUDError):
    """Exceção para erros de login robô."""

    def __init__(self, exception: Exception, bot_execution_id: str = None) -> None:
        """Inicializador da instância de exceção."""
        message = "\n".join(traceback.format_exception(exception))
        super().__init__(message)
        self.message = "Erro Ao realizar login.\n Exception: " + message

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message
