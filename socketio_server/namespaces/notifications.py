"""Socket.IO namespace for notification events and management."""

import socketio

from socketio_server.types import ASyncServerType


class NotificationNamespace(socketio.AsyncNamespace):
    """Socket.IO namespace for handling notification events between server and clients."""

    namespace: str
    server: ASyncServerType

    async def on_connect(self, sid: str, environ: dict[str, str]) -> None:
        """Handle client connection event for notifications.

        Args:
            sid: The session ID of the client.
            environ: The WSGI environment dictionary for the connection.

        """
        # Optionally, send a welcome notification or log the connection

    async def on_disconnect(self, sid: str) -> None:
        """Handle client disconnection event for notifications.

        Args:
            sid: The session ID of the client.

        """
        # Optionally, log the disconnection

    async def on_send_notification(self, sid: str, data: dict) -> None:
        """Receive a notification from a client and broadcast or process it.

        Args:
            sid: The session ID of the client sending the notification.
            data: Dictionary containing notification details (e.g., message, type).

        """
        # Example: broadcast notification to all clients except sender
        await self.emit("notification", data, skip_sid=sid)

    async def notify(self, data: dict) -> None:
        """Send a notification to all connected clients.

        Args:
            data: Dictionary containing notification details (e.g., message, type).

        """
        await self.emit("notification", data)
