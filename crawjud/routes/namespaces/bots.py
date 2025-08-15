"""Socket.IO namespace for notification events and management."""

from quart_socketio import Namespace

from crawjud.api import db
from crawjud.decorators.api import verify_jwt_websocket
from crawjud.interfaces import ASyncServerType
from crawjud.interfaces.credentials import (
    CredendialDictSelect,
)
from crawjud.models.bots import BotsCrawJUD, Credentials


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
    async def on_bots_list(self) -> list:
        """Retorne uma lista de bots cadastrados no sistema.

        Args:
            Nenhum.

        Returns:
            list: Lista de dicionários contendo dados dos bots.

        Raises:
            Nenhuma exceção explícita.

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
                for k, v in bot.__dict__.items()
                if not k.startswith("_")
            }
            bots.append(bot_data)

        return bots

    @verify_jwt_websocket
    async def on_bot_credentials_select(
        self,
    ) -> dict[str, list[CredendialDictSelect]]:
        """Retorne um dicionário de listas de credenciais disponíveis por sistema.

        Args:
            Nenhum.

        Returns:
            dict[str, list[CredendialDictSelect]]: Dicionário onde a chave é o nome
            do sistema e o valor é uma lista de opções de credenciais.

        Raises:
            Nenhuma exceção explícita.

        """
        query = db.session.query(Credentials).all()

        # Inicializa o dicionário de credenciais com opções padrão para cada sistema
        sistemas = ["elaw", "esaj", "projudi", "pje"]
        credentials = {
            sistema: [
                CredendialDictSelect(
                    value=None,
                    text="Selecione uma Credencial",
                    disabled=True,
                ),
            ]
            for sistema in sistemas
        }

        # Adiciona as credenciais consultadas ao dicionário correspondente
        for item in query:
            sistema = item.system.lower()
            if sistema in credentials:
                credentials[sistema].append(
                    CredendialDictSelect(value=item.id, text=item.nome_credencial),
                )

        return credentials
