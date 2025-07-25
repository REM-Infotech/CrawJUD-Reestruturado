"""Módulo de gerenciamento de logs CrawJUD."""

from ._async import AsyncPrintMessage
from ._normal import PrintMessage

__all__ = ["PrintMessage", "AsyncPrintMessage"]
