"""Modulo de gerenciamento de tarefas do Celery."""

from celery_app import app
from celery_app.tasks import _email, bot, files
from celery_app.tasks.bot import message
from celery_app.tasks.bot._main import BotTask

app.register_task(BotTask.run_task)

__all__ = ["bot", "_email", "files", "message"]
