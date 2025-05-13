"""Modulo de gerenciamento de tarefas do Celery."""

from celery import shared_task


@shared_task
def send_email(to: str, message: str) -> None:
    """Send an email to the specified recipient."""


@shared_task
def initialize_bot(bot_name: str, bot_system: str) -> None:
    """Inicializa uma execução de robô."""
