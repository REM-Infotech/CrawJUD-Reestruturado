"""Socket.IO namespace for notification events and management."""

from quart_socketio import Namespace

from api import db
from api.models.bots import BotsCrawJUD
from api.types import ASyncServerType


class BotsNamespace(Namespace):
    """Socket.IO namespace for handling bot events between server and clients."""

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

    async def on_bots_list(self) -> None:
        """Handle request for the list of bots.

        This method can be used to send the list of bots to the client.
        """
        # Example: send a list of bots to all connected clients

        bots = []

        for bot in db.session.query(BotsCrawJUD).all():
            bot_data = {}
            for k, v in list(bot.__dict__.items()):
                if k.startswith("_"):
                    continue
                if isinstance(v, bytes):
                    v = v.decode("utf-8")
                bot_data.update({k: v})

            bots.append(bot_data)

        return bots

    async def on_setup_form(self) -> None:  # noqa: D102
        pass
