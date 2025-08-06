# noqa: D100
from functools import wraps
from typing import Any, AnyStr, ParamSpec, TypeVar
from uuid import uuid4

from dotenv import dotenv_values
from socketio import SimpleClient

from crawjud.bot import ClassBot

TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

environ = dotenv_values()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}


def wrap_init(cls: type[ClassBot]) -> type[TClassBot]:  # noqa: D103
    original_init = cls.__init__

    @wraps(original_init)
    def novo_init(
        self: TClassBot,
        *args: TBotSpec.args,
        **kwargs: TBotSpec.kwargs,
    ) -> None:
        print(f"Instanciando {cls.__name__} com args: {args}, kwargs: {kwargs}")
        original_init(self)

    cls.__init__ = novo_init
    return cls


def wrap_cls(cls: type[ClassBot]) -> type[TClassBot]:  # noqa: D103
    original_cls = cls

    @wraps(wrap_cls)
    def novo_init(
        self: TClassBot = None,
        *args: TBotSpec.args,
        **kwargs: TBotSpec.kwargs,
    ) -> None:
        with SimpleClient(
            reconnection_attempts=20,
            reconnection_delay=5,
        ) as sio:
            # Conecta ao servidor Socket.IO com o URL, namespace e cabeçalhos especificados.
            kw = kwargs.copy()
            sio.connect(
                url=server,
                namespace=namespace,
                headers=headers,
                transports=transports,
            )
            cls = original_cls()

            @sio.client.on("stopbot", namespace=namespace)
            def stop_bot(*args: Any, **kwargs: Any) -> None:
                cls.stop_bot = True

            sio.emit(
                "join_room",
                data={"data": {"room": kwargs.get("pid", uuid4().hex)}},
            )

            cls.sio = sio
            return cls.execution(*args, **kw)

    return novo_init
