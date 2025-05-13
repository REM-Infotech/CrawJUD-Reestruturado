"""Módulo Celery App do CrawJUD Automatização."""

import logging
from logging.config import dictConfig
from os import getenv
from pathlib import Path
from typing import AnyStr

from celery import Celery
from celery.signals import after_setup_logger

from celery_app.addons import worker_name_generator
from celery_app.addons.logger import dict_config
from celery_app.resources.load_config import Config


@after_setup_logger.connect
def config_loggers(
    logger: logging.Logger,
    *args: AnyStr,
    **kwargs: AnyStr,
) -> None:
    """Configure and alter the Celery logger for the application.

    This function updates the Celery logger configuration based on environment
    variables and custom logging settings. It ensures that the Celery logger uses
    the desired log level and handlers derived from the application's logging configuration.

    Args:
        logger (logging.Logger): The logger instance to configure.
        *args (AnyType): Positional arguments.
        **kwargs (AnyType): Keyword arguments, may include a 'logger' instance to be configured.

    """
    logger_name = f"{worker_name_generator()}_celery"
    log_path = Path().cwd().joinpath("temp", "logs")
    log_path.mkdir(exist_ok=True, parents=True)
    log_file = log_path.joinpath(f"{logger_name}.log")
    log_file.touch(exist_ok=True)

    log_level = logging.INFO
    if getenv("DEBUG", "False").lower() == "true":
        log_level = logging.DEBUG

    config, _ = dict_config(LOG_LEVEL=log_level, LOGGER_NAME=logger_name, FILELOG_PATH=log_file)

    dictConfig(config)
    # Alter the Celery logger using the provided logger from kwargs if available.
    logger.setLevel(log_level)
    # Clear existing handlers and add the ones from the new configuration.
    logger.handlers.clear()
    configured_logger = logging.getLogger(logger_name.replace("_", "."))
    for handler in configured_logger.handlers:
        logger.addHandler(handler)


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


app = make_celery()
application = app
