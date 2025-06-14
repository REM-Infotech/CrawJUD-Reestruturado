"""Namespaces de bot."""

from typing import AnyStr

import engineio
import socketio
from quart_socketio import Namespace


class ASyncServerType(socketio.AsyncServer):
    """ClassType for AsyncServer."""

    eio: engineio.AsyncServer


class BotsNamespace(Namespace):
    """Namespace bots."""

    namespace: str
    server: ASyncServerType

    async def save_session(self, sid: str, session: dict[str, AnyStr], namespace: str | None = None) -> None:
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

    async def on_connect(self, sid: str, environ: dict[str, str]) -> None:
        """Evento de conexão."""
        session = {"sid": sid}

        await self.save_session(sid, session, self.namespace)

    async def on_disconnect(self, sid: str, reason: str) -> None:
        """Evento de desconexão."""

    async def on_join_room(self, sid: str, data: dict[str, str], environ: dict[str, str] | None = None) -> None:
        """JOIN ROOM."""
        room = data.get("pid")
        await self.enter_room(sid=sid, room=room, namespace=self.namespace)

    async def on_log_execution(self, sid: str, data: dict[str, str]) -> None:
        """Evento de recebimento de log."""
        await self.emit("log_execution", data, room=data["pid"])
