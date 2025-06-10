"""Socket.IO namespaces package for managing file, bot, and notification events.

This module exposes all available namespaces for direct import.
"""

from quart_socketio import SocketIO

from .files import FileNamespaces
from .logs import BotsNamespace
from .notifications import NotificationNamespace

__all__ = [
    "FileNamespaces",
    "BotsNamespace",
    "NotificationNamespace",
]


async def register_namespaces(io: SocketIO) -> None:
    """Register all namespaces with the Socket.IO server.

    This function registers the file, bot, and notification namespaces
    with the provided Socket.IO instance.

    :param io: The Socket.IO instance to register namespaces with.
    """
    await io.register_namespace(FileNamespaces())
    await io.register_namespace(BotsNamespace())
    await io.register_namespace(NotificationNamespace())
