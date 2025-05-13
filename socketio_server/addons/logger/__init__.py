"""Módulo de gerenciamento de logs do CrawJUD."""

import logging
from typing import Any

handlers = {
    "file_handler": {
        "class": "crawjud.addons.logger.handlers.FileHandler",
        "level": logging.INFO,
        "formatter": "json",
        "filename": "app.log",
        "maxBytes": 1024,
        "backupCount": 1,
    },
    "redis_handler": {
        "class": "crawjud.addons.logger.handlers.RedisHandler",
        "level": logging.INFO,
        "formatter": "json",
    },
}

formatters = (
    {
        "default": {
            "format": "%(levelname)s:%(name)s:%(message)s",
        },
        "json": {
            "()": "crawjud.addons.logger.formatters.JsonFormatter",
        },
    },
)


def dict_config(**kwargs: str | int) -> tuple[dict[str, Any], str]:
    """Gerador de configurações do logging."""
    log_level: int = kwargs.get("LOG_LEVEL", logging.INFO)
    logger_name: str = kwargs.get("LOGGER_NAME", __name__)
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": log_level,
            "handlers": list(handlers.keys()),
        },
        "handlers": handlers,
        "formatters": formatters,
        "loggers": {
            logger_name: {
                "level": log_level,
                "handlers": list(handlers.keys()),
                "propagate": False,
            },
        },
    }

    return config, logger_name
