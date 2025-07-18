"""Socket.IO namespace for notification events and management."""

from quart_socketio import Namespace

from api import db
from api.interface.credentials import (
    CredendialDictSelect,
)
from api.models.bots import BotsCrawJUD, Credentials
from api.types import ASyncServerType
from api.wrapper import verify_jwt_websocket


class BotsNamespace(Namespace):
    """Socket.IO namespace for handling bot events between server and clients."""

    namespace: str
    server: ASyncServerType

    @verify_jwt_websocket
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

    @verify_jwt_websocket
    async def on_bots_list(self) -> None:
        """Handle request for the list of bots.

        This method can be used to send the list of bots to the client.
        """
        # Example: send a list of bots to all connected clients

        bots = []

        def decode_str(v: str | bytes) -> str:
            if isinstance(v, bytes):
                v = v.decode("utf-8")

            return v

        for bot in db.session.query(BotsCrawJUD).all():
            bot_data = {
                k: decode_str(v)
                for k, v in list(bot.__dict__.items())
                if not k.startswith("_")
            }
            bots.append(bot_data)

        return bots

    @verify_jwt_websocket
    async def on_bot_credentials_select(self) -> None:  # noqa: D102
        query = db.session.query(Credentials).all()

        # Inicializa o dicionário de credenciais com opções padrão para cada sistema
        sistemas = ["elaw", "esaj", "projudi", "pje"]
        credentials = {
            sistema: [
                CredendialDictSelect(
                    value=None, text="Selecione uma Credencial", disabled=True
                )
            ]
            for sistema in sistemas
        }

        # Adiciona as credenciais consultadas ao dicionário correspondente
        for item in query:
            sistema = item.system.lower()
            if sistema in credentials:
                credentials[sistema].append(
                    CredendialDictSelect(value=item.id, text=item.nome_credencial)
                )

        return credentials
