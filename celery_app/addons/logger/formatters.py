"""Módulo de classes de formatadores de logs."""

import json
import logging


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
