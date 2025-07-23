# noqa: D100
from typing import Any, TypeVar

from celery import Task
from celery.app import shared_task as shared

TSharedTask = TypeVar("SharedTask", bound=Task)


class SharedTask:  # noqa: ANN002, ANN003, D101, D103
    def __call__(self, *args: Any, **kwargs: Any) -> TSharedTask:  # noqa: D102
        return shared(*args, **kwargs)
