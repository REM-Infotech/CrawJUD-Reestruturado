"""Namespaces de bot."""

import engineio
import socketio
from quart import request, session
from quart_socketio import Namespace


class ASyncServerType(socketio.AsyncServer):
    """ClassType for AsyncServer."""

    eio: engineio.AsyncServer


class LogsNamespace(Namespace):
    """Namespace bots."""

    namespace: str
    server: ASyncServerType

    async def on_connect(self) -> None:
        """Evento de conexão."""
        sid = request.sid
        await self.save_session(sid=sid, session=session)

    async def on_disconnect(self) -> None:
        """Evento de desconexão."""

    async def on_stop_signal(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003, D102
        message_data = dict(list((await request.form).items()))
        await self.emit("stop_signal", data=message_data, room=message_data["pid"])

    async def on_join_room(self) -> None:
        """JOIN ROOM."""
        sid = request.sid
        data = await request.form
        await self.enter_room(sid=sid, room=data["room"], namespace=self.namespace)

    async def on_log_execution(self) -> None:
        """Evento de recebimento de log."""
        message_data = dict(list((await request.form).items()))
        await self.emit("log_execution", data=message_data, room=message_data["pid"])
