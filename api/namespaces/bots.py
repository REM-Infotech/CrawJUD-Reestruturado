"""Socket.IO namespace for notification events and management."""

import json
from pathlib import Path

import aiofiles
from quart_socketio import Namespace

from api import db
from api.models.bots import BotsCrawJUD, Credentials
from api.namespaces.interface.credentials import (
    CredendialDictSelect,
    CredendialsDict,
    CredendialsSystemDict,
)
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

        if Path("cache_bots.json").exists():
            async with aiofiles.open("cache_bots.json", "r", encoding="utf-8") as f:
                return json.loads(await f.read())

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

        if not Path("cache_bots.json").exists():
            async with aiofiles.open("cache_bots.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(bots))

        return bots

    @verify_jwt_websocket
    async def on_bot_credentials_select(self) -> None:  # noqa: D102
        query = db.session.query(Credentials).all()

        credentials = CredendialsSystemDict(elaw=[], esaj=[], projudi=[], pje=[])

        for item in query:
            credentials.get(item.system.lower(), []).append(
                CredendialDictSelect(value=item.id, text=item.nome_credencial)
            )

        return credentials

    @verify_jwt_websocket
    async def on_bot_credentials_list(self) -> None:  # noqa: D102
        query = db.session.query(Credentials).all()

        credentials: list[CredendialsDict] = []

        for item in query:
            loginmethod = (
                "Usuário/Senha"
                if item.login_method == "pw"
                else "Certificado difital"
            )
            credentials.append(
                CredendialsDict(
                    id=item.id,
                    nome_credencial=item.nome_credencial,
                    system=item.system,
                    login_method=loginmethod,
                )
            )

        return credentials
