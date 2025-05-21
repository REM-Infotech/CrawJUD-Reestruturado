"""Modulo de gerenciamento de tarefas do Celery."""

from celery_app.tasks import bot, email, files

__all__ = ["bot", "email", "files"]
