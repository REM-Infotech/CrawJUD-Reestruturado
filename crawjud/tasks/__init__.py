"""Modulo de gerenciamento de tarefas do Celery."""

from crawjud import bots
from crawjud.tasks import email, files, message

__all__ = ["bots", "email", "files", "message"]
