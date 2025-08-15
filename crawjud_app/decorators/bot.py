"""Decora classes e métodos relacionados ao bot para integração com Socket.IO.

Este módulo fornece:
- wrap_init: decora o método __init__ para exibir informações de instanciação;
- wrap_cls: decora classes bot para execução sob controle de conexão Socket.IO.
"""

from contextlib import suppress
from functools import wraps
from uuid import uuid4

from dotenv import dotenv_values
from socketio import SimpleClient
from tqdm import tqdm

from crawjud.controllers.bots.master.bot_head import ClassBot

environ = dotenv_values()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


class _CustomSimpleClass[T](SimpleClient):
    def emit(self, event: T, data: T = None) -> None:
        with suppress(Exception):
            return super().emit(event, data)

    def connect(
        self,
        url: T,
        headers: T = ...,
        auth: T = None,
        transports: T = None,
        namespace: T = "/",
        socketio_path: T = "socket.io",
        wait_timeout: T = 5,
    ) -> None:
        with suppress(Exception):
            return super().connect(
                url,
                headers,
                auth,
                transports,
                namespace,
                socketio_path,
                wait_timeout,
            )


def wrap_init[T](cls: type[ClassBot]) -> type[T]:
    """Decora o método __init__ de uma classe para exibir informações de instancia.

    Args:
        cls (type[ClassBot]): Classe do bot a ser decorada.

    Returns:
        type[T]: Classe decorada com __init__ modificado.

    """
    original_init = cls.__init__

    @wraps(original_init)
    def novo_init(
        self: T = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        return original_init(self, *args, **kwargs)

    cls.__init__ = novo_init
    return cls


def wrap_cls[T](cls: type[ClassBot]) -> type[T]:
    """Decora uma classe bot para executar métodos sob controle de conexão Socket.IO.

    Args:
        cls (T): Classe do bot a ser decorada.

    Returns:
        type[T]: Classe decorada com execução controlada via Socket.IO.

    """
    original_cls = cls

    @wraps(wrap_cls)
    def novo_init(
        self: T | None = None,
        *args: T,
        **kwargs: T,
    ) -> None:
        with _CustomSimpleClass(
            reconnection_attempts=20,
            reconnection_delay=5,
        ) as sio:
            # Conecta ao servidor Socket.IO com o URL,
            # namespace e cabeçalhos especificados.
            sio.connect(
                url=server,
                namespace=namespace,
                headers=headers,
                transports=transports,
                wait_timeout=300,
            )
            cls = original_cls()
            sio.emit(
                "join_room",
                data={"data": {"room": kwargs.get("pid", uuid4().hex)}},
            )

            def stop_bot[T](*args: T, **kwargs: T) -> None:
                tqdm.write(str(args))
                tqdm.write(str(kwargs))
                cls.stop_bot = True

            sio.client.on("stopbot", namespace=namespace, handler=stop_bot)

            cls.sio = sio

            if self:
                return cls.execution(current_task=self, *args, **kwargs)

            return cls.execution(self, *args, **kwargs)

    return novo_init
