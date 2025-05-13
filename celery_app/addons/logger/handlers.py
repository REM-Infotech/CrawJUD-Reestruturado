"""Custom logging handlers."""

import json
import logging
import logging.handlers
from os import environ
from pathlib import Path

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

        load_dotenv(str(Path(__file__).cwd().joinpath("celery_app", ".env")))
        kwrgs = environ

        self.LIST_LOGS_REDIS = kwrgs["LIST_LOGS_REDIS"]
        self.URI_REDIS = kwrgs["URI_REDIS"]
        self.DATABASE = int(kwrgs["DATABASE"])

        self.client = redis.Redis.from_url(url=self.URI_REDIS, db=self.DATABASE)  # Conexão com o Redis

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the log record to Redis."""
        try:
            log_entry = self.format(record)  # Formata o log conforme configurado
            self.client.rpush(self.LIST_LOGS_REDIS, log_entry)  # Adiciona à lista no Redis
        except Exception:
            self.handleError(record)  # Captura erros ao salvar no Redis


class FileHandler(logging.handlers.RotatingFileHandler):
    """Custom logging handler to send logs to a file."""

    filename = "app.logs"
    max_bytes = 1024
    backup_count = 1

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record to JSON."""
        log_data = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, "%Y-%m-%d %H:%M:%S"),
            "module": record.module,
        }
        return json.dumps(log_data)
