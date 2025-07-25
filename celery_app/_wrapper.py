from typing import Any, Callable, Optional, ParamSpec, TypeVar

from celery import shared_task as share

T = TypeVar("SharedTask", bound=Any)
P = ParamSpec("SharedParamSpecTask", bound=Any)


def shared_task(*args: Any, **kwargs: Any) -> Callable[P, Optional[T]]:  # noqa: D103
    return share(*args, **kwargs)
