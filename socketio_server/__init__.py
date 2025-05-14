"""Módulo gerenciador do servidor SocketIO CrawJUD."""

import asyncio
from os import environ

from redis import Redis
from socketio import AsyncRedisManager, AsyncServer

from socketio_server.addons import check_allowed_origin
from socketio_server.namespaces.bot_message import BotsNamespace

with_redis = environ.get("WITH_REDIS", "false").lower() == "true"

if with_redis:
    redis_url = environ["SOCKETIO_REDIS"]
    redis_manager = AsyncRedisManager(url=redis_url)
    redis_app = Redis.from_url(redis_url)


async def register_namespaces(sio: AsyncServer) -> None:
    """Função para registrar namespaces."""
    sio.register_namespace(BotsNamespace("/logs"))


async def create_socketioserver() -> AsyncServer:
    """Construtor para o SocketIO Server."""
    sio = AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=check_allowed_origin,
        client_manager=redis_manager if with_redis else None,
        ping_interval=25,
        ping_timeout=10,
        namespaces=["/bot", "/logs"],
    )

    return sio


sio = asyncio.run(create_socketioserver())
