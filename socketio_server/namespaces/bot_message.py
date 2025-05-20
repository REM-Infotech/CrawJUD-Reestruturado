"""Namespaces de bot."""

import socketio

session = {}


class BotsNamespace(socketio.AsyncNamespace):
    """Namespace bots."""

    namespace: str

    def on_connect(self, sid: str, environ: str) -> None:
        """Evento de conexão."""
        self.save_session(sid, session, self.namespace)

    def on_disconnect(self, sid: str, reason: str) -> None:
        """Evento de desconexão."""

    async def on_log_message(self, sid: str, data: dict[str, str]) -> None:
        """Evento de recebimento de log."""
        await self.emit("log_message", data)

    async def on_log_execution(self, sid: str, data: dict[str, str]) -> None:
        """Evento de recebimento de log."""
        await self.emit("log_message", data, room=data["pid"])
