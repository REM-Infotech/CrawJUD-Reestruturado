"""Módulo de controle de exceptions dos bots."""

from crawjud.exceptions import BaseCrawJUDError


class StartError(Exception):
    """Exception raised for errors that occur during the start of the bot."""


class ExecutionError(BaseCrawJUDError):
    """Exception raised for errors during CrawJUD execution.

    This exception is a subclass of BaseCrawJUDError and is used to indicate
    that an error occurred during the execution of a CrawJUD process.

    Methods:
        __instancecheck__(instance: Exception) -> bool:
            Check if the instance is an exception.
        __str__() -> str:
            Return the string representation of the exception.

    """
