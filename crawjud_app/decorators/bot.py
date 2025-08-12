"""Decora classes e métodos relacionados ao bot para integração com Socket.IO.

Este módulo fornece:
- wrap_init: decora o método __init__ para exibir informações de instanciação;
- wrap_cls: decora classes bot para execução sob controle de conexão Socket.IO.
"""

from functools import wraps
from uuid import uuid4

from dotenv import dotenv_values
from socketio import SimpleClient
from tqdm import tqdm

from crawjud_app.abstract.bot import ClassBot

environ = dotenv_values()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


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
        tqdm.write(
            f"Instanciando {cls.__name__} com args: {args}, kwargs: {kwargs}",
        )
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
        with SimpleClient(
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

            return cls.execution(self, *args, **kwargs)

    return novo_init
