"""Socket.IO namespace for notification events and management."""

from quart_socketio import Namespace

from api.types import ASyncServerType


class SystemNamespace(Namespace):
    """Socket.IO namespace for handling system events between server and clients."""

    namespace: str
    server: ASyncServerType

    async def on_connect(self) -> None:
        """Handle client connection event for notifications.

        Args:
            sid: The session ID of the client.
            environ: The WSGI environment dictionary for the connection.

        """
        # Optionally, send a welcome notification or log the connection

    async def on_disconnect(self) -> None:
        """Handle client disconnection event for notifications.

        Args:
            sid: The session ID of the client.

        """
        # Optionally, log the disconnection

    async def on_number_bots(self) -> None:
        """Handle request for the number of bots.

        This method can be used to send the current number of bots to the client.
        """
        # Example: send the number of bots to all connected clients
        return 25
