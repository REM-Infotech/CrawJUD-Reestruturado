from __future__ import annotations

from asyncio import iscoroutinefunction
from asyncio import run as run_async
from typing import Any, AnyStr, Generic, ParamSpec, TypeVar  # noqa: F401

from celery.app.task import Task as TaskBase

from celery_app.custom._canvas import subtask  # noqa: F401
from celery_app.types._celery._canvas import (  # noqa: F401
    AsyncResult,
    EagerResult,
    Signature,
)

T = TypeVar("T", bound=AnyStr)
P = ParamSpec("P")
R = TypeVar("R")


class ContextTask(TaskBase):
    abstract = True
    contains_classmethod = False

    def _run(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        kwargs["current_task"] = self

        if iscoroutinefunction(self.run):
            return run_async(self.run(*args, **kwargs))  # noqa: B026

        return self.run(*args, **kwargs)  # noqa: B026

    def signature(
        self, args: Any = None, *starargs: Any, **starkwargs: Any
    ) -> Signature:
        """Create signature.

        Returns:
            :class:`~celery.signature`:  object for
                this task, wrapping arguments and execution options
                for a single task invocation.

        """
        starkwargs.setdefault("app", self.app)
        return subtask(self, args, *starargs, **starkwargs)

    def subtask(
        self,
        args: Any = None,
        *starargs: Any,
        **starkwargs: Any,
    ) -> Signature:
        """Create signature.

        Returns:
            :class:`~celery.signature`:  object for
                this task, wrapping arguments and execution options
                for a single task invocation.

        """
        star_arg = starargs
        star_kwarg = starkwargs

        return subtask(self, args, *star_arg, **star_kwarg)

    def apply_async(
        self,
        args: tuple[str, Any] = None,
        kwargs: dict[str, Any] = None,
        task_id: str = None,
        producer: str = None,
        link: str = None,
        link_error: str = None,
        shadow: str = None,
        **options: Any,
    ) -> AsyncResult | EagerResult:
        return super().apply_async(
            args, kwargs, task_id, producer, link, link_error, shadow, **options
        )

    def __call__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
        return self._run(*args, **kwargs)
