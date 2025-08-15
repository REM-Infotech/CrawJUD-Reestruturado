"""Módulo Celery App do CrawJUD Automatização."""

import importlib

from crawjud.custom import AsyncCelery as Celery
from crawjud.utils.load_config import Config

app = Celery(__name__)


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    importlib.import_module("crawjud_app.tasks", __package__)

    config = Config.load_config()

    app.conf.update(config.celery_config)

    app.conf.update(
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",
    )

    return app


app_celery = make_celery()
