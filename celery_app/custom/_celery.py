import asyncio
import importlib
from typing import AnyStr

from celery import Celery


class AsyncCelery(Celery):
    def __init__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
        super().__init__(*args, **kwargs)
        self.patch_task()

        if "app" in kwargs:
            self.init_app(kwargs["app"])

    def patch_task(self) -> None:
        TaskBase = self.Task  # noqa: N806

        class ContextTask(TaskBase):
            abstract = True
            contains_classmethod = False

            def get_cls(self, qualname: str, module_name: str) -> object:
                _module = importlib.import_module(module_name)
                cls: object = getattr(_module, qualname, None)
                if cls is None:
                    raise ImportError(
                        f"Class {qualname} not found in module {module_name}"
                    )
                return cls

            def _run(self, *args: AnyStr, **kwargs: AnyStr) -> None:
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

                if asyncio.iscoroutinefunction(self.run):
                    return asyncio.run(self.run(*args, **kwargs))  # noqa: B026

                return self.run(task=self, *args, **kwargs)  # noqa: B026

            def __call__(self, *args: AnyStr, **kwargs: AnyStr) -> None:
                return self._run(*args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app: AnyStr) -> None:
        self.app = app

        conf = {}
        for key in app.config.keys():
            if key[0:7] == "CELERY_":
                conf[key[7:].lower()] = app.config[key]

        if (
            "broker_transport_options" not in conf
            and conf.get("broker_url", "")[0:4] == "sqs:"
        ):
            conf["broker_transport_options"] = {"region": "eu-west-1"}

        self.config_from_object(conf)
