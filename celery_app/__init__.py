"""Módulo Celery App do CrawJUD Automatização."""

from celery import Celery
from kombu import Queue  # noqa: F401

from celery_app.resources.load_config import Config


def make_celery() -> Celery:
    """Create and configure a Celery instance with Quart application context.

    Args:
        app (Quart): The Quart application instance.

    Returns:
        Celery: Configured Celery instance.

    """
    celery = Celery(__name__)
    config = Config.load_config()

    celery.conf.update(config.celery_config)

    class ContextTask(celery.Task):
        def __call__(
            self,
            *args: tuple,
            **kwargs: dict,
        ) -> any:  # -> any:
            return self.run(*args, **kwargs)

    celery.Task = ContextTask

    celery.conf.update(
        # task_queues=CELERY_QUEUES,
        # task_routes=CELERY_ROUTES,
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",
    )

    return celery
