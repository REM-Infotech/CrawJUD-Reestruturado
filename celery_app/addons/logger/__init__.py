"""Módulo de gerenciamento de logs do celery_app."""

import logging
from typing import Any


def dict_config(**kwargs: str | int) -> tuple[dict[str, Any], str]:
    """Gerador de configurações do logging."""
    _log_level: int = kwargs.get("LOG_LEVEL", logging.INFO)
    logger_name: str = kwargs.get("LOGGER_NAME", __name__)

    handlers_config = {
        "file_handler": {
            "class": "celery_app.addons.logger.handlers.FileHandler",
            "level": logging.DEBUG,
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 8196,
            "backupCount": 10,
        },
    }
    handlers_config["file_handler"]["level"] = logging.DEBUG
    handlers_config["file_handler"]["maxBytes"] = 40960
    handlers_config["file_handler"]["backupCount"] = 10
    handlers_config["file_handler"]["filename"] = kwargs["FILELOG_PATH"]

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "root": {
            "level": logging.DEBUG,
            "handlers": list(handlers_config.keys()),
        },
        "handlers": handlers_config,
        "formatters": {
            "default": {
                "format": "%(levelname)s:%(name)s:%(message)s",
            },
            "json": {
                "()": "celery_app.addons.logger.handlers.JsonFormatter",
            },
        },
        "loggers": {
            logger_name: {
                "level": logging.DEBUG,
                "handlers": list(handlers_config.keys()),
                "propagate": False,
            },
        },
    }

    return config, logger_name
