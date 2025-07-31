from typing import Any, AnyStr, Callable, Optional, ParamSpec, TypeVar

from celery import shared_task as share

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


def classmethod_shared_task(
    *task_args: Any,
    **task_kwargs: Any,
) -> Any:
    """
    Crie um decorador para permitir o uso de shared_task em métodos de classe.

    Args:
        *task_args: Argumentos posicionais para o shared_task.
        **task_kwargs: Argumentos nomeados para o shared_task.

    Returns:
        Callable[..., classmethod]: Função decorada como classmethod e shared_task.

    """

    def decorator(func: Callable[..., R]) -> classmethod:
        # Aplica o shared_task na função
        task = share(*task_args, **task_kwargs)(func)
        task.contains_classmethod = True
        # Retorna como classmethod
        return task

    if len(task_args) == 1 and callable(task_args[0]):
        # Se o primeiro argumento for uma função, aplica diretamente
        return classmethod_shared_task()(task_args[0])

    return decorator


T = TypeVar("SharedTask", bound=Any)
P = ParamSpec("SharedParamSpecTask", bound=Any)


def shared_task(*args: Any, **kwargs: Any) -> Callable[P, Optional[T]]:  # noqa: D103
    return share(*args, **kwargs)
