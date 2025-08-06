"""Módulo Celery App do CrawJUD Automatização."""

import importlib
import logging
import re
from contextlib import suppress
from logging.config import dictConfig
from os import environ, getenv
from pathlib import Path
from threading import Thread
from typing import AnyStr

from celery.signals import after_setup_logger
from socketio import Client

from celery_app.custom import AsyncCelery as Celery
from celery_app.resources.load_config import Config
from utils.logger import dict_config

app = Celery(__name__)
sio = Client(
    reconnection_attempts=20,
    reconnection_delay=5,
    reconnection_delay_max=10,
    reconnection=True,
)

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}

with suppress(Exception):
    sio.connect(
        url=server,
        namespaces=["/logsbot", "/bots"],
        headers=headers,
        transports=transports,
    )

    Thread(target=sio.wait, daemon=True).start()


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
    logger_name = environ.get(
        "WORKER_NAME", str(re.sub(r"[^a-zA-Z0-9]", "_", "celery_app"))
    )
    log_path = Path().cwd().joinpath("temp", "logs")
    log_path.mkdir(exist_ok=True, parents=True)
    log_file = log_path.joinpath(f"{logger_name}.log")
    log_file.touch(exist_ok=True)

    log_level = logging.INFO
    if getenv("DEBUG", "False").lower() == "true":
        log_level = logging.INFO

    config, _ = dict_config(
        LOG_LEVEL=log_level, LOGGER_NAME=logger_name, FILELOG_PATH=log_file
    )

    logger.handlers.clear()
    dictConfig(config)
    # Alter the Celery logger using the provided logger from kwargs if available.
    logger.setLevel(log_level)
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
    importlib.import_module("celery_app.tasks", __package__)

    config = Config.load_config()

    app.conf.update(config.celery_config)

    # class ContextTask(celery.Task):
    #     def __call__(
    #         self,
    #         *args: tuple,
    #         **kwargs: dict,
    #     ) -> any:  # -> any:
    #         return self.run(*args, **kwargs)

    # celery.Task = ContextTask

    app.conf.update(
        # task_queues=CELERY_QUEUES,
        # task_routes=CELERY_ROUTES,
        task_default_queue="default",
        task_default_exchange="default",
        task_default_routing_key="default",
    )

    return app


app_celery = make_celery()
