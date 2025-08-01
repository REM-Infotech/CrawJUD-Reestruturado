from typing import AnyStr, ParamSpec, TypeVar

from celery_app.custom._task import ContextTask
from celery_app.types._celery._canvas import Signature

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


class Task(Signature, ContextTask): ...
