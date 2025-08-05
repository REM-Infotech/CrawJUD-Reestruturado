from functools import wraps
from typing import AnyStr, ParamSpec, TypeVar

from crawjud.common.bot import ClassBot

TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)


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
