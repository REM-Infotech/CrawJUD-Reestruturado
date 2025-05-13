"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from celery_app import shared_task
from celery_app.addons.mail import Mail

if TYPE_CHECKING:
    from celery_app.types import TReturnMessageMail


@shared_task
def send_email(subject: str, to: str, message: str, files_path: list[str] = None) -> TReturnMessageMail:
    """Send an email to the specified recipient."""
    mail = Mail()
    mail.message["Subject"] = subject
    mail.message["To"] = to
    mail.message.attach(message)

    if len(files_path) > 0:
        for file in files_path:
            mail.attach_file(file)

    mail.send_message(to=to)

    return "E-mail enviado com sucesso!"


@shared_task
def initialize_bot(bot_name: str, bot_system: str, path_config: str) -> None:
    """Inicializa uma execução de robô."""
    bot = import_module(f"crawjud.bots.{bot_system.lower()}.{bot_name.lower()}", __package__)

    class_bot = getattr(bot, bot_name.capitalize(), None)
    class_bot.initialize(bot_name=bot_name, bot_system=bot_system, path_config=path_config)
