"""Custom logging handlers."""

import json
import logging
import logging.handlers
import time
from os import environ
from typing import AnyStr

import click
import redis
from dotenv import load_dotenv


class RedisHandler(logging.Handler):
    """Custom logging handler to send logs to Redis."""

    LIST_LOGS_REDIS: str
    URI_REDIS: str
    DATABASE: int

    def __init__(self, **kwrgs: str | int) -> None:
        """Initialize the RedisHandler."""
        super().__init__()

        load_dotenv()
        kwrgs = environ

        self.LIST_LOGS_REDIS = kwrgs.get(
            "LIST_LOGS_REDIS", __package__.replace(".", "_")
        )
        self.URI_REDIS = kwrgs["REDIS_URI"]
        self.DATABASE = int(kwrgs["REDIS_DB"])

        self.client = redis.Redis.from_url(
            url=self.URI_REDIS, db=self.DATABASE
        )  # Conexão com o Redis

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record to Redis."""
        try:
            log_entry = self.format(record)  # Formata o log conforme configurado
            self.client.rpush(
                self.LIST_LOGS_REDIS, log_entry
            )  # Adiciona à lista no Redis
        except Exception:
            self.handleError(record)  # Captura erros ao salvar no Redis


class FileHandler(logging.handlers.RotatingFileHandler):
    """Custom logging handler to send logs to a file."""

    filename = "app.logs"
    maxBytes = 1024  # noqa: N815
    backupCount = 1  # noqa: N815

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record to JSON."""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.format_time(record, "%Y-%m-%d %H:%M:%S"),
            "module": record.module,
        }
        return json.dumps(log_data)

    def format_time(self, record: logging.LogRecord, datefmt: str = None) -> AnyStr:
        """
        Return the creation time of the specified LogRecord as formatted text.

        This method should be called from format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        in formatters to provide for any specific requirement, but the
        basic behaviour is as follows: if datefmt (a string) is specified,
        it is used with time.strftime() to format the creation time of the
        record. Otherwise, an ISO8601-like (or RFC 3339-like) format is used.
        The resulting string is returned. This function uses a user-configurable
        function to convert the creation time to a tuple. By default,
        time.localtime() is used; to change this for a particular formatter
        instance, set the 'converter' attribute to a function with the same
        signature as time.localtime() or time.gmtime(). To change it for all
        formatters, for example if you want all logging times to be shown in GMT,
        set the 'converter' attribute in the Formatter class.
        """
        ct = time.localtime(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime(self.default_time_format, ct)
            if self.default_msec_format:
                s = self.default_msec_format % (s, record.msecs)
        return s


class _ColorFormatter(logging.Formatter):
    grey = click.style("%(message)s", fg=(1, 66, 66), reset=True)
    green = click.style("%(message)s", fg="green", reset=True)
    yellow = click.style("%(message)s", fg="yellow", reset=True)
    red = click.style("%(message)s", fg="red")
    bold_red = click.style("%(message)s", fg="red", bold=True, reset=True)
    reset = click.style("%(message)s", fg="reset", reset=True)

    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: grey,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
        "uvicorn": green,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)

        if hasattr(record, "color_message"):
            # codes = re.findall(r"\x1b\[(\d+)m", record.color_message)
            # color = codes[0] or self.green
            # log_fmt = f"\x1b[{color}m" + self.format_msg + self.reset
            record.msg = record.color_message

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class JsonFormatter(logging.Formatter):
    """Json Formatter for logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record to JSON."""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "module": record.module,
            "module_name": record.name,
        }
        return json.dumps(log_data)
