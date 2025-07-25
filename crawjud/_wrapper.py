from typing import AnyStr, Callable, ParamSpec, TypeVar

from common.bot import ClassBot

TClassBot = TypeVar("TClassBot", bound=ClassBot)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)


def wrap_init(cls: type[TClassBot]) -> type[TClassBot]:  # noqa: D103
    original_init: Callable[TBotSpec, None] = cls.__init__

    def novo_init(
        self: TClassBot,
        *args: TBotSpec.args,
        **kwargs: TBotSpec.kwargs,
    ) -> None:
        print(f"Instanciando {cls.__name__} com args: {args}, kwargs: {kwargs}")
        original_init(self, *args, **kwargs)

    cls.__init__ = novo_init
    return cls
