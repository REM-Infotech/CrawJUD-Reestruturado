"""Modulo de gerenciamento de tarefas do Celery."""

from crawjud import bots
from tasks import _email, bot, files, message

__all__ = ["bot", "_email", "files", "message", "bots"]
