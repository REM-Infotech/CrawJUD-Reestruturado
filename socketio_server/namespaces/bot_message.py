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

    async def save_session(self, sid: str, session: dict[str, AnyStr], namespace: str = None) -> None:
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

    async def on_connect(self, sid: str, environ: str) -> None:
        """Evento de conexão."""
        session = {"sid": sid}
        await self.save_session(sid, session, self.namespace)

    async def on_disconnect(self, sid: str, reason: str) -> None:
        """Evento de desconexão."""

    async def on_log_message(self, sid: str, data: dict[str, str]) -> None:
        """Evento de recebimento de log."""
        path_log_msg = await Path(__file__).parent.resolve()
        path_log_msg = path_log_msg.joinpath("temp", "log_msg")
        await path_log_msg.mkdir(exist_ok=True, parents=True)
        await self.emit("log_message", data)


# @sio.on("connect", namespace="/logs")
# async def connect(sid: str, environ: str) -> None:
#     """Evento de conexão."""
#     sio.save_session(sid, session, "/logs")


# @sio.on("disconnect", namespace="/logs")
# async def disconnect(sid: str, reason: str) -> None:
#     """Evento de desconexão."""


# @sio.on("log_message", namespace="/logs")
# async def log_message(sid: str, data: dict[str, str]) -> None:
#     """Evento de recebimento de log."""
#     path_log_msg = await Path(__file__).parent.resolve()
#     path_log_msg = path_log_msg.joinpath("temp", "log_msg")
#     await path_log_msg.mkdir(exist_ok=true, parents=true)
#     async with await path_log_msg.joinpath(f"{sid}.log").open("w") as f:
#         await f.write(data)
#     await sio.emit("log_message", data)
