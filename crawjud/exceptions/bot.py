"""Módulo de controle de exceptions dos bots."""

import logging
import traceback

from crawjud.exceptions import BaseCrawJUDError


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""

    def __init__(
        self,
        exception: Exception,
        bot_execution_id: str = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = (
            message
            + "\n Exception: "
            + "\n".join(traceback.format_exception_only(exception))
        )

        if not bot_execution_id:
            bot_execution_id = __name__

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class ExecutionError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        if exception:
            self.message += "\n Exception: " + "\n".join(
                traceback.format_exception_only(exception)
            )

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class LoginSystemError(BaseCrawJUDError):
    """Exceção para erros de login robô."""

    def __init__(
        self,
        exception: Exception,
        bot_execution_id: str,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = (
            message
            + "\n Exception: "
            + "\n".join(traceback.format_exception_only(exception))
        )
        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class ProcNotFoundError(BaseCrawJUDError):
    """Exception de Processo não encontrado."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        if exception:
            self.message += "\n Exception: " + "\n".join(
                traceback.format_exception_only(exception)
            )

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class GrauIncorretoError(BaseCrawJUDError):
    """Exception de Grau Incorreto/Não informado."""

    def __init__(
        self,
        exception: Exception,
        bot_execution_id: str,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = (
            message
            + "\n Exception: "
            + "\n".join(traceback.format_exception_only(exception))
        )
        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class SaveError(BaseCrawJUDError):
    """Exception para erros de salvamento de Formulários/Arquivos."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        if exception:
            self.message = (
                self.message
                + "\n Exception: "
                + "\n".join(traceback.format_exception_only(exception))
            )

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class FileError(BaseCrawJUDError):
    """Exception para erros de envio de arquivos."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de envio de arquivos."""
        self.message = message

        if exception:
            self.message = (
                self.message
                + "\n Exception: "
                + "\n".join(traceback.format_exception_only(exception))
            )

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class CadastroParteError(BaseCrawJUDError):
    """Exception para erros de cadastro de parte no Elaw."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message
        if exception:
            self.message += "\n Exception: " + "\n".join(
                traceback.format_exception_only(exception)
            )
        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class MoveNotFoundError(BaseCrawJUDError):
    """Exception para erros de movimentações não encontradas."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message
        if exception:
            self.message += "\n Exception: " + "\n".join(
                traceback.format_exception_only(exception)
            )
        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class PasswordError(BaseCrawJUDError):
    """Exception para erros de senha."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de senha."""
        self.message = message
        if exception:
            self.message += "\n Exception: " + "\n".join(
                traceback.format_exception_only(exception)
            )
        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class NotFoundError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        if exception:
            self.message += "\n Exception: " + "\n".join(
                traceback.format_exception_only(exception)
            )

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message
