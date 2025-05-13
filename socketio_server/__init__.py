"""Módulo gerenciador do servidor SocketIO CrawJUD."""

from os import getenv

from redis import Redis
from socketio import AsyncRedisManager, AsyncServer

from socketio_server.addons import check_allowed_origin


def create_socketioserver() -> tuple[AsyncServer, Redis]:
    """Construtor para o SocketIO Server."""
    with_redis = getenv("WITH_REDIS", "false")
    host_redis = getenv("REDIS_HOST")
    pass_redis = getenv("REDIS_PASSWORD")
    port_redis = getenv("REDIS_PORT")
    database_redis = getenv("REDIS_DB_LOGS")
    database_redis_io = getenv("REDIS_DB_IO")
    redis_manager = AsyncRedisManager(url=f"redis://:{pass_redis}@{host_redis}:{port_redis}/{database_redis_io}")
    redis_app = Redis(host=host_redis, port=port_redis, password=pass_redis, db=database_redis)

    io = AsyncServer(
        async_mode="asgi",
        cors_allowed_origins=check_allowed_origin,
        client_manager=redis_manager if with_redis.lower() == "True" else None,
        ping_interval=25,
        ping_timeout=10,
        namespaces=["/bot", "/logs"],
    )

    return io, redis_app


create_server = create_socketioserver()
io = create_server[0]
redis_app = create_server[1]
