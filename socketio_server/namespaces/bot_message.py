"""Namespaces de bot."""

from typing import AnyStr

import engineio
import socketio
from anyio import Path


class ASyncServerType(socketio.AsyncServer):
    """ClassType for AsyncServer."""

    eio: engineio.AsyncServer


class BotsNamespace(socketio.AsyncNamespace):
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

    async def on_connect(self, sid: str, environ: dict[str, str], test: str) -> None:
        """Evento de conexão."""
        session = {"sid": sid}

        room = environ.get("HTTP_ROOM")

        dict_items_query = {
            item.split("=")[0]: item.split("=")[1] for item in list(environ.get("QUERY_STRING").split("&"))
        }

        if dict_items_query.get("pid"):
            room = dict_items_query.get("pid")

        if room:
            await self.enter_room(sid=sid, room=room, namespace=self.namespace)
        await self.save_session(sid, session, self.namespace)

    async def on_disconnect(self, sid: str, reason: str) -> None:
        """Evento de desconexão."""

    async def on_log_message(self, sid: str, data: dict[str, str]) -> None:
        """Evento de recebimento de log."""
        path_log_msg = await Path(__file__).parent.resolve()
        path_log_msg = path_log_msg.joinpath("temp", "log_msg")
        await path_log_msg.mkdir(exist_ok=True, parents=True)
        await self.emit("log_message", data)

    async def on_log_execution(self, sid: str, data: dict[str, str]) -> None:
        """Evento de recebimento de log."""
        await self.emit("log_execution", data, room=data["pid"])
