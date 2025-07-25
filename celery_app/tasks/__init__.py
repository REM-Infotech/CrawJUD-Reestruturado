"""Modulo de gerenciamento de tarefas do Celery."""

from celery_app import app
from celery_app.tasks import _email, bot, files
from celery_app.tasks.bot import _main, message

__all__ = ["bot", "_email", "files", "message", "_main", "app"]
