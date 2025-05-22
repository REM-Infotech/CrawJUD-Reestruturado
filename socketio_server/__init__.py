"""Módulo gerenciador do servidor SocketIO CrawJUD."""

from os import environ

from quart import Quart
from redis import Redis
from socketio import ASGIApp, AsyncRedisManager, AsyncServer

from socketio_server.addons import check_allowed_origin
from socketio_server.middleware import ProxyFixMiddleware
from socketio_server.namespaces import BotsNamespace

app = Quart(__name__)

with_redis = environ.get("WITH_REDIS", "false").lower() == "true"

if with_redis:
    redis_url = environ["SOCKETIO_REDIS"]
    redis_manager = AsyncRedisManager(url=redis_url)
    redis_app = Redis.from_url(redis_url)


async def register_namespaces(sio: AsyncServer) -> None:
    """Função para registrar namespaces."""
    async with app.app_context():
        sio.register_namespace(BotsNamespace("/logs"))


async def create_socketioserver() -> ASGIApp:
    """Construtor para o SocketIO Server."""
    sio = AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=check_allowed_origin,
        client_manager=redis_manager if with_redis else None,
        ping_interval=25,
        ping_timeout=10,
        namespaces=["/bot", "/logs"],
        transports=["websocket"],
    )

    await register_namespaces(sio)
    app.asgi_app = ProxyFixMiddleware(app.asgi_app)
    app.extensions["socketio"] = sio
    return ASGIApp(sio, app)
