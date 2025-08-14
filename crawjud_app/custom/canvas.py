"""Forneça utilitários para criação e manipulação de subtasks Celery neste módulo.

Este módulo disponibiliza funções para facilitar a criação
de subtasks e manipulaçãode assinaturas Celery, promovendo a
reutilização e padronização no uso de tarefas assíncronas.
"""

from __future__ import annotations

from typing import AnyStr

from celery.utils.abstract import CallableSignature

from crawjud.interface.types.celery.canvas import Signature


def subtask(
    varies: str,
    *args: AnyStr,
    **kwargs: AnyStr,
) -> Signature:
    """Crie e retorne uma subtask Celery.

    Args:
        varies (str): Nome da tarefa, dicionário de assinatura ou instância Signature.
        *args (AnyStr): Argumentos posicionais para a subtask.
        **kwargs (AnyStr): Argumentos nomeados para a subtask.

    Returns:
        Signature: Instância de assinatura Celery configurada.



    """
    app = kwargs.get("app")

    if not app:
        from celery import current_app

        app = current_app
        kwargs["app"] = app

    if isinstance(varies, str):
        tsk = app.tasks[varies]
        return tsk.subtask(*args, **kwargs)

    if isinstance(varies, dict):
        if isinstance(varies, CallableSignature):
            return varies.clone()
        return Signature.from_dict(varies, app=app)

    return Signature(varies, *args, **kwargs)
