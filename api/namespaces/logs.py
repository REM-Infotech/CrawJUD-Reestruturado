"""Namespaces de bot."""

from __future__ import annotations

from contextlib import suppress

import engineio
import socketio
from quart import request, session
from quart_socketio import Namespace
from redis_om import NotFoundError

from addons.printlogs._interface import MessageLog as MessageLogDict
from api.models.logs import MessageLog


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

    async def on_load_cache(self) -> None:
        """Carrega o cache."""
        _data = dict(list((await request.form).items()))
        message = await self.log_redis(pid=_data["pid"])
        await self.emit("load_cache", data=message, room=_data["pid"])

    async def on_log_execution(self) -> None:
        """Evento de recebimento de log."""
        _data = dict(list((await request.form).items()))
        message = await self.log_redis(pid=_data["pid"], message=_data)
        await self.emit("log_execution", data=message, room=_data["pid"])

    async def _calc_success_errors(self, message: MessageLogDict) -> None:
        """Calcula os valores de sucesso e erros."""
        message["success"] = message.get("success", 0)
        message["errors"] = message.get("errors", 0)
        message["remaining"] = message.get("total", 0) - message["success"]

        if message["type"] == "error":
            message["errors"] += 1
        elif message["type"] == "success":
            message["success"] += 1

        return message

    async def log_redis(self, pid: str, message: MessageLogDict = None) -> None:
        """Carrega/atualiza o log no Redis."""
        log = await self._query_logs(pid)
        if log:
            if not message:
                return log.model_dump()

            log.update(**message)

        elif not log:
            message = await self._calc_success_errors(message)
            log = MessageLog(**message)
            log.save()

    async def _query_logs(self, pid: str) -> MessageLog | None:
        with suppress(NotFoundError, Exception):
            log = MessageLog.get(pid)

            return log
