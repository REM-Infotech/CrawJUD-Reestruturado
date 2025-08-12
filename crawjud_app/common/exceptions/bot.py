"""Módulo de controle de exceptions dos bots."""

import traceback

from crawjud_app.common.exceptions import BaseCrawJUDError

MessageError = "Erro ao executar operaçao: "


def formata_msg(exc: Exception | None = None) -> str:  # noqa: D103
    if exc:
        return "\n Exception: " + "\n".join(traceback.format_exception_only(exc))

    return ""


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""

    def __init__(
        self,
        message: str = MessageError,
        exc: Exception | None = None,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class ExecutionError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(
        self,
        message: str = MessageError,
        exc: Exception | None = None,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        if message == "Erro ao executar operaçao: " and exc:
            self.message = message + "\n".join(traceback.format_exception(exc))

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class LoginSystemError(BaseCrawJUDError):
    """Exceção para erros de login robô."""

    def __init__(
        self,
        message: str = MessageError,
        exc: Exception | None = None,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class ProcNotFoundError(BaseCrawJUDError):
    """Exception de Processo não encontrado."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class GrauIncorretoError(BaseCrawJUDError):
    """Exception de Grau Incorreto/Não informado."""

    def __init__(
        self,
        exc: Exception,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class SaveError(BaseCrawJUDError):
    """Exception para erros de salvamento de Formulários/Arquivos."""

    def __init__(
        self,
        exc: Exception,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class FileError(BaseCrawJUDError):
    """Exception para erros de envio de arquivos."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de envio de arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class CadastroParteError(BaseCrawJUDError):
    """Exception para erros de cadastro de parte no Elaw."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class MoveNotFoundError(BaseCrawJUDError):
    """Exception para erros de movimentações não encontradas."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class PasswordError(BaseCrawJUDError):
    """Exception para erros de senha."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de senha."""
        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class NotFoundError(BaseCrawJUDError):
    """Exceção para erros de execução do robô."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message


class FileUploadError(BaseCrawJUDError):
    """Exception para erros de upload de arquivos."""

    def __init__(
        self,
        exc: Exception | None = None,
        message: str = MessageError,
    ) -> None:
        """Exception para erros de upload de arquivos."""
        self.message = message

        self.message = message + formata_msg(exc)

        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem de erro.

        Returns:
            str: Mensagem de erro formatada.

        """
        return self.message
