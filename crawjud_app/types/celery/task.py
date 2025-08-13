"""Defina tipos personalizados para integração de tasks Celery.

Este módulo fornece:
- Classe Task: integra Signature e ContextTask para uso avançado no Celery.
"""

from typing import AnyStr, ParamSpec, TypeVar

from crawjud_app.custom.task import ContextTask
from crawjud_app.types.celery.canvas import Signature

P = ParamSpec("P")
R = TypeVar("R")
TClassBot = TypeVar("TClassBot", bound=object)
TBotSpec = ParamSpec("TBotSpec", bound=AnyStr)

class_set = set()


class Task(Signature, ContextTask):
    """Type (Task) personalizada integrando Signature e ContextTask para o Celery.

    Args:
        Signature (Signature): Assinatura da tarefa Celery.
        ContextTask (ContextTask): Task com contexto customizado.

    Returns:
        Task: Instância de task personalizada para uso no Celery.

    """
