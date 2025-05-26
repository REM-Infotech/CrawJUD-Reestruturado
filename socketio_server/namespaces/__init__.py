"""Socket.IO namespaces package for managing file, bot, and notification events.

This module exposes all available namespaces for direct import.
"""

from .files import FileNamespaces
from .logs import BotsNamespace
from .notifications import NotificationNamespace

__all__ = [
    "FileNamespaces",
    "BotsNamespace",
    "NotificationNamespace",
]
