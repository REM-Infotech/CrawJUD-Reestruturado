from __future__ import annotations

import importlib
from asyncio import iscoroutinefunction
from asyncio import run as run_async
from typing import Any, AnyStr, Generic, ParamSpec, TypeVar  # noqa: F401

from celery.app.task import Task as TaskBase

from celery_app.custom._canvas import subtask  # noqa: F401
from celery_app.types._celery._canvas import Signature  # noqa: F401

T = TypeVar("T", bound=AnyStr)
P = ParamSpec("P")
R = TypeVar("R")


class ContextTask(TaskBase):
    abstract = True
    contains_classmethod = False

    def get_cls(self, qualname: str, module_name: str) -> T:
        _module = importlib.import_module(module_name)
        cls = getattr(_module, qualname, None)
        if cls is None:
            raise ImportError(f"Class {qualname} not found in module {module_name}")
        return cls

    def _run(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        _annotations = self.__annotations__
        # if len(self.__wrapped__.__qualname__.split(".")) > 1:
        #     # If the task is a classmethod, we need to get the class
        #     cls = self.get_cls(
        #         self.__wrapped__.__qualname__.split(".")[0],
        #         self.__wrapped__.__module__,
        #     )

        #     kwargs.update({"cls": cls})
        #     if len(args) > 0 and str(type(args[0])) == str(type(cls)):
        #         # If the first argument is an instance of the class, we can use it
        #         kwargs.pop("cls")
        #     # Create an instance of the class

        if "current_task" in _annotations:
            kwargs["current_task"] = self

        elif "task" in _annotations:
            kwargs["task"] = self

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

    def __call__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
        return self._run(*args, **kwargs)
