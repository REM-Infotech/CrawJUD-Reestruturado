"""Namespaces de bot."""

from typing import AnyStr

import engineio
import socketio
from quart_socketio import Namespace


class ASyncServerType(socketio.AsyncServer):
    """ClassType for AsyncServer."""

    eio: engineio.AsyncServer


class LogsNamespace(Namespace):
    """Namespace bots."""

    namespace: str
    server: ASyncServerType

    async def save_session(
        self, sid: str, session: dict[str, AnyStr], namespace: str | None = None
    ) -> None:
        """Store the user session for a client.

        :param sid: The session id of the client.
        :param session: The session dictionary.
        :param namespace: The Socket.IO namespace. If this argument is omitted
                          the default namespace is used.
        """
        namespace = namespace or "/"
        eio_sid = self.server.manager.eio_sid_from_sid(sid, namespace)
        eio_session = await self.server.eio.get_session(eio_sid)
        eio_session[namespace] = session

    async def on_connect(self) -> None:
        """Evento de conexão."""

    async def on_disconnect(self) -> None:
        """Evento de desconexão."""

    async def on_join_room(self) -> None:
        """JOIN ROOM."""

    async def on_log_execution(self) -> None:
        """Evento de recebimento de log."""
        await self.emit("log_execution")
