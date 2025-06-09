"""Modulo de gerenciamento de tarefas do Celery."""

from celery_app.tasks import _email, bot, files

__all__ = ["bot", "_email", "files"]
