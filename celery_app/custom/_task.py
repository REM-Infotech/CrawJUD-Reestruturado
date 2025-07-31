import importlib
from asyncio import iscoroutinefunction
from asyncio import run as run_async
from typing import AnyStr, Generic, ParamSpec, TypeVar, Union, cast

from celery.app.task import Task as TaskBase
from celery.canvas import Signature as __Signature
from celery.utils.abstract import CallableSignature

from celery_app.custom._celery import AsyncCelery
from celery_app.types._celery import Signature

T = TypeVar("T", bound=AnyStr)
P = ParamSpec("P")
R = TypeVar("R")
TSig = TypeVar("TSig", bound=Union[CallableSignature, Signature])


class ContextTask(TaskBase):
    abstract = True
    contains_classmethod = False

    def get_cls(self, qualname: str, module_name: str) -> object:
        _module = importlib.import_module(module_name)
        cls: object = getattr(_module, qualname, None)
        if cls is None:
            raise ImportError(f"Class {qualname} not found in module {module_name}")
        return cls

    def _run(self, *args: Generic[T], **kwargs: Generic[T]) -> None:
        annotations = self.__annotations__
        if self.contains_classmethod:
            # If the task is a classmethod, we need to get the class
            cls = self.get_cls(
                self.__wrapped__.__qualname__.split(".")[0],
                self.__wrapped__.__module__,
            )
            if not isinstance(cls, type):
                raise TypeError(f"{cls} is not a class")

            kwargs.update({"cls": cls})

            # Create an instance of the class

        if "current_task" in annotations or "task" in annotations:
            kwargs.update({"task": self})
            kwargs["task"] = self

        if iscoroutinefunction(self.run):
            return run_async(self.run(*args, **kwargs))  # noqa: B026

        return self.run(*args, **kwargs)  # noqa: B026

    def __call__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
        return self._run(*args, **kwargs)


def subtask(
    varies: str | TSig,
    *args: AnyStr,
    **kwargs: AnyStr,
) -> Generic[TSig]:
    """Create new signature.

    - if the first argument is a signature already then it's cloned.
    - if the first argument is a dict, then a Signature version is returned.

    Returns:
        Signature: The resulting signature.

    """
    app: AsyncCelery = kwargs.get("app")
    if isinstance(varies, dict):
        if isinstance(varies, CallableSignature):
            return cast(Signature, varies.clone())
        return cast(Signature, __Signature.from_dict(varies, app=app))
    return cast(Signature, __Signature(varies, *args, **kwargs))
