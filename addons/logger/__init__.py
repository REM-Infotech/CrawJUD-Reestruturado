"""Módulo de gerenciamento de logs da api."""

import logging
from typing import Any


def dict_config(**kwargs: str | int) -> tuple[dict[str, Any], str]:
    """Gerador de configurações do logging."""
    _log_level: int = kwargs.get("LOG_LEVEL", logging.INFO)
    logger_name: str = kwargs.get("LOGGER_NAME", __name__)

    handlers_config = {
        "file_handler": {
            "class": "addons.logger.handlers.FileHandler",
            "level": logging.INFO,
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 1024,
            "backupCount": 1,
        },
        "stream_handler": {
            "class": "logging.StreamHandler",
            "level": logging.INFO,
            "formatter": "color",  # Usa o novo formatter colorido
        },
        "redis_handler": {
            "class": "addons.logger.handlers.RedisHandler",
            "level": logging.INFO,
            "formatter": "json",
        },
    }
    handlers_config["file_handler"]["level"] = logging.INFO
    handlers_config["file_handler"]["maxBytes"] = 40960
    handlers_config["file_handler"]["backupCount"] = 5
    handlers_config["file_handler"]["filename"] = kwargs["FILELOG_PATH"]

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": logging.INFO,
            "handlers": list(handlers_config.keys()),
        },
        "handlers": handlers_config,
        "formatters": {
            "default": {
                "format": "%(message)s",
            },
            "json": {
                "()": "addons.logger.handlers.JsonFormatter",
            },
            "color": {
                "()": "addons.logger.handlers._ColorFormatter",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "loggers": {
            logger_name: {
                "level": logging.INFO,
                "handlers": list(handlers_config.keys()),
                "propagate": False,
            },
        },
    }

    return config, logger_name
