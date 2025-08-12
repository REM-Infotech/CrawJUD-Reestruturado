from __future__ import annotations

from typing import AnyStr, TypeVar

from celery.utils.abstract import CallableSignature

from crawjud_app.types._celery._canvas import Signature

T = TypeVar("T", bound=AnyStr)


def subtask(
    varies: str,
    *args: AnyStr,
    **kwargs: AnyStr,
) -> Signature:
    """Create new subtask Signature.

    - if the first argument is a subtask Signature already then it's cloned.
    - if the first argument is a dict, then a subtask Signature version is returned.

    Returns:
        Task: The resulting task.

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
