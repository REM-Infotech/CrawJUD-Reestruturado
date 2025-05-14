"""Módulo de gerenciamento de logs do socketio server."""

import logging
from typing import AnyStr


def dict_config(**kwargs: str | int) -> tuple[dict[str, AnyStr], str]:
    """Gerador de configurações do logging."""
    log_level: int = kwargs.get("LOG_LEVEL", logging.INFO)
    logger_name: str = kwargs.get("LOGGER_NAME", __name__)

    handlers_config = {
        "file_handler": {
            "class": "socketio_server.addons.logger.handlers.FileHandler",
            "level": logging.INFO,
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 1024,
            "backupCount": 1,
        },
        # "redis_handler": {
        #     "class": "socketio_server.addons.logger.handlers.RedisHandler",
        #     "level": logging.INFO,
        #     "formatter": "json",
        # },
    }
    handlers_config["file_handler"]["level"] = log_level
    handlers_config["file_handler"]["maxBytes"] = 40960
    handlers_config["file_handler"]["backupCount"] = 5
    handlers_config["file_handler"]["filename"] = kwargs["FILELOG_PATH"]

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": log_level,
            "handlers": list(handlers_config.keys()),
        },
        "handlers": handlers_config,
        "formatters": {
            "default": {
                "format": "%(levelname)s:%(name)s:%(message)s",
            },
            "json": {
                "()": "socketio_server.addons.logger.handlers.JsonFormatter",
            },
        },
        "loggers": {
            logger_name: {
                "level": log_level,
                "handlers": list(handlers_config.keys()),
                "propagate": False,
            },
        },
    }

    return config, logger_name
