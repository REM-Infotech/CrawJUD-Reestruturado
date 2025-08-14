"""Custom logging handlers."""

import json
import logging
import logging.handlers
import time
from contextlib import suppress
from os import environ

import click
import redis
from dotenv import load_dotenv

from crawjud.utils.models.logs import ModelRedisHandler

FSTRING_MESSAGE = "%(message)s"

grey = click.style(FSTRING_MESSAGE, fg=(15, 194, 150), reset=True)
green = click.style(FSTRING_MESSAGE, fg="green", reset=True)
yellow = click.style(FSTRING_MESSAGE, fg="yellow", reset=True)
red = click.style(FSTRING_MESSAGE, fg="red")
bold_red = click.style(FSTRING_MESSAGE, fg="red", bold=True, reset=True)
reset = click.style(FSTRING_MESSAGE, fg="reset", reset=True)

FORMATS = {
    logging.INFO: grey,
    logging.WARNING: yellow,
    logging.ERROR: red,
    logging.CRITICAL: bold_red,
    "uvicorn": green,
}

default_time_format = "%Y-%m-%d %H:%M:%S"
default_msec_format = "%s.%03d"


def _format_time(
    record: logging.LogRecord,
    datefmt: str | None = None,
) -> str:
    ct = time.localtime(record.created)
    if datefmt:
        s = time.strftime(datefmt, ct)
    else:
        s = time.strftime(default_time_format, ct)
        if default_msec_format:
            s = default_msec_format % (s, record.msecs)
    return s


def _format_json(record: logging.LogRecord) -> str:
    """Formata o registro de log para o formato JSON.

    Args:
        record (logging.LogRecord): Registro de log a ser formatado.

    Returns:
        str: Registro de log formatado em JSON.

    """
    return json.dumps({
        "level": record.levelname,
        "message": record.getMessage(),
        "time": _format_time(record, "%Y-%m-%d %H:%M:%S"),
        "module": record.module,
        "module_name": record.name,
    })


class RedisHandler[T](logging.Handler):
    """Custom logging handler to send logs to Redis."""

    LIST_LOGS_REDIS: str
    URI_REDIS: str
    DATABASE: int

    def __init__(self, **kwargs: T) -> None:
        """Initialize the RedisHandler."""
        super().__init__()

        load_dotenv()
        env_vars = environ  # Use a new variable for environment variables

        self.LIST_LOGS_REDIS = env_vars.get(
            "LIST_LOGS_REDIS",
            __package__.replace(".", "_"),
        )
        self.URI_REDIS = env_vars["REDIS_URI"]
        self.DATABASE = int(env_vars["REDIS_DB"])

        self.client = redis.Redis.from_url(
            url=self.URI_REDIS,
            db=self.DATABASE,
        )  # Conexão com o Redis

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record to Redis."""
        with suppress(Exception):
            log_entry = self.format(record)  # Formata o log conforme configurado
            ModelRedisHandler(**dict(json.loads(log_entry))).save()


class FileHandler(logging.handlers.RotatingFileHandler):
    """Custom logging handler to send logs to a file."""

    filename = "app.logs"
    maxBytes = 1024  # noqa: N815
    backupCount = 1  # noqa: N815

    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log para o formato JSON.

        Args:
            record (logging.LogRecord): Registro de log a ser formatado.

        Returns:
            str: Registro de log formatado em JSON.

        """
        return _format_json(record)


class ColorFormatter(logging.Formatter):
    """Formata registros de log com cores conforme o nível de severidade."""

    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log com cores conforme o nível.

        Args:
            record (logging.LogRecord): Registro de log a ser formatado.

        Returns:
            str: Registro de log formatado com cores.

        """
        log_fmt = FORMATS.get(record.levelno)

        if hasattr(record, "color_message"):
            record.msg = record.color_message

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class JsonFormatter(logging.Formatter):
    """Json Formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Formata o registro de log para o formato JSON.

        Args:
            record (logging.LogRecord): Registro de log a ser formatado.

        Returns:
            str: Registro de log formatado em JSON.

        """
        return _format_json(record)
