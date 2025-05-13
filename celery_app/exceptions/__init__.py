"""Módulo de tratamento de exceptions do celery_app."""

from __future__ import annotations


class BaseExceptionCeleryAppError(Exception):
    """Base exception class for Celery app errors."""
