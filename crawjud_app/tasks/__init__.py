"""Modulo de gerenciamento de tarefas do Celery."""

from crawjud_app import bots
from crawjud_app.tasks import email, files, message

__all__ = ["bots", "email", "files", "message"]
