"""Módulo de exceptions elaw."""

from __future__ import annotations

import logging
import traceback

from crawjud.exceptions import BaseCrawJUDError


class ElawError(BaseCrawJUDError):
    """Exception genérico de erros Elaw."""

    def __init__(
        self,
        exception: Exception,
        bot_execution_id: str,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + "\n Exception: " + "\n".join(traceback.format_exception_only(exception))
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
        exception: Exception,
        bot_execution_id: str,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + "\n Exception: " + "\n".join(traceback.format_exception_only(exception))
        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message


class AdvogadoError(BaseCrawJUDError):
    """Exception para erros de Inserção/Cadastro de advogado no elaw."""

    def __init__(
        self,
        bot_execution_id: str,
        exception: Exception = None,
        message: str = "Erro ao executar operaçao: ",
    ) -> None:
        """Exception para erros de salvamento de Formulários/Arquivos."""
        self.message = message + "\n Exception: "

        if exception:
            self.message = self.message + "\n Exception: " + "\n".join(traceback.format_exception_only(exception))

        logger = logging.getLogger(bot_execution_id)
        logger.error(message)
        super().__init__(message)

    def __str__(self) -> str:
        """Retorna a mensagem."""
        return self.message
