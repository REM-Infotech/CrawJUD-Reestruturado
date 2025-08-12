"""Fornece decoradores para tarefas compartilhadas do Celery e métodos de classe.

Este módulo contém decoradores tipados para facilitar o uso do Celery
em funções e métodos de classe, garantindo integração com type annotations.
"""

from collections.abc import Callable
from typing import Any, AnyStr, ParamSpec, TypeVar

from celery import shared_task as share

from crawjud_app.types._celery._task import Task

from ._bot import wrap_cls, wrap_init

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("SharedTask", bound=Any)
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


def shared_task[T](*args: T, **kwargs: T) -> Task | Callable[..., Task]:
    """Crie um decorador do shared_task com Type Annotations.

    Args:
        *args: Argumentos posicionais para o shared_task.
        **kwargs: Argumentos nomeados para o shared_task.

    Returns:
        Callable[..., Task]: Função decorada como shared_task.

    """

    def decorator(func: Callable[P, R]) -> Task:
        # Aplica o shared_task na função
        task = share(*args, **kwargs)(func)
        task.contains_classmethod = True
        # Retorna como classmethod
        return task

    if len(args) == 1 and callable(args[0]):
        # Se o primeiro argumento for uma função, aplica diretamente
        return shared_task(*args, **kwargs)(args[0])

    return decorator


def classmethod_shared_task[T](
    *args: T,
    **kwargs: T,
) -> Task | Callable[P, Task]:
    """Crie um decorador para permitir o uso de shared_task em métodos de classe.

    Args:
        *args: Argumentos posicionais para o shared_task.
        **kwargs: Argumentos nomeados para o shared_task.

    Returns:
        Task | Callable[P, Task]: Função decorada

    """

    def decorator(func: Callable[P, R]) -> Task:
        # Aplica o shared_task na função
        task = share(*args, **kwargs)(func)
        task.contains_classmethod = True
        # Retorna como classmethod
        return task

    if len(args) == 1 and callable(args[0]):
        # Se o primeiro argumento for uma função, aplica diretamente
        return classmethod_shared_task(*args, **kwargs)(args[0])

    return decorator


__all__ = [
    "classmethod_shared_task",
    "shared_task",
    "wrap_cls",
    "wrap_init",
]
