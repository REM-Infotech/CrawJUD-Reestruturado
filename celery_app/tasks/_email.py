"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from celery_app._wrapper import shared_task
from celery_app.addons.mail import Mail
from celery_app.types import ReturnFormataTempo

if TYPE_CHECKING:
    from celery_app.types import TReturnMessageMail

T = TypeVar("AnyValue", bound=ReturnFormataTempo)


@shared_task(name="send_email")
def send_email(
    subject: str,
    to: str,
    message: str,
    files_path: list[str] = None,
    *args: Generic[T],
    **kwargs: Generic[T],
) -> TReturnMessageMail:
    """Send an email to the specified recipient."""
    mail = Mail.construct()
    mail.message["Subject"] = subject
    mail.message["To"] = to
    mail.message.attach(message)

    if len(files_path) > 0:
        for file in files_path:
            mail.attach_file(file)

    mail.send_message(to=to)

    return "E-mail enviado com sucesso!"
