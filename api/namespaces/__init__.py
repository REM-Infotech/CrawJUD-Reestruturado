"""Socket.IO namespaces package for managing file, bot, and notification events.

This module exposes all available namespaces for direct import.
"""

from typing import AnyStr  # noqa: F401

from quart import current_app, request, websocket  # noqa: F401
from quart_socketio import Namespace, SocketIO

from api.namespaces.bots import BotsNamespace
from api.namespaces.system import SystemNamespace

from .files import FileNamespaces
from .logs import LogsNamespace
from .notifications import NotificationNamespace

__all__ = [
    "FileNamespaces",
    "LogsNamespace",
    "NotificationNamespace",
]


class MasterNamespace(Namespace):
    """Base class for all namespaces in the application.

    This class serves as a base for defining custom namespaces
    that handle specific events and interactions within the application.
    """

    async def on_teste(self) -> None:
        """Handle a test event.

        This method is an example of how to handle custom events.
        It can be overridden in subclasses to implement specific logic.

        """
        session = self.server.session(websocket.sid, self.namespace)  # noqa: B018, F841
        print(request)  # noqa: T201

    async def on_disconnect(self) -> None:
        """Handle client disconnection event.

        Args:
            sid: The session ID of the client.
            reason: The reason for disconnection.

        """
        print(websocket, request)  # noqa: T201


async def register_namespaces(io: SocketIO) -> None:
    """Register all namespaces with the Socket.IO server.

    This function registers the file, bot, and notification namespaces
    with the provided Socket.IO instance.

    :param io: The Socket.IO instance to register namespaces with.
    """
    namespaces = [
        SystemNamespace("/system", io),
        MasterNamespace("/master", io),
        FileNamespaces("/files", io),
        LogsNamespace("/logsbot", io),
        BotsNamespace("/bots", io),
        NotificationNamespace("/notifications", io),
    ]

    for namespace in namespaces:
        await io.register_namespace(namespace)
