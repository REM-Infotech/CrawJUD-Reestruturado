"""Módulo de gerenciamento de logs CrawJUD."""

from __future__ import annotations

import logging
from datetime import datetime
from os import environ
from typing import TYPE_CHECKING

from socketio import AsyncClient, Client

if TYPE_CHECKING:
    from crawjud.common.bot import ClassBot

_namespace = environ["SOCKETIO_SERVER_NAMESPACE"]


class PrintLogs:  # noqa: D101
    _sio: Client | AsyncClient = None
    namespace: str = _namespace
    url_server: str
    row: int
    pid: str
    message: str
    _logger: logging.Logger = logging.getLogger(__name__)
    _total_rows: int = 0
    _start_time: datetime
    _bot_instance: ClassBot = None

    @property
    def bot_instance(self) -> ClassBot:  # noqa: D102
        return self._bot_instance

    @bot_instance.setter
    def bot_instance(self, inst: ClassBot) -> None:
        self._bot_instance = inst

    @property
    def start_time(self) -> datetime:  # noqa: D102
        return self._start_time

    @start_time.setter
    def start_time(self, time_set: datetime) -> None:
        self._start_time = time_set

    @property
    def logger(self) -> logging.Logger:  # noqa: D102
        return self._logger

    @logger.setter
    def logger(self, new_logger: logging.Logger) -> None:
        self._logger = new_logger

    @property
    def total_rows(self) -> int:  # noqa: D102
        return self._total_rows

    @total_rows.setter
    def total_rows(self, new_value: int) -> None:
        self._total_rows = new_value

    @property
    def row(self) -> int:  # noqa: D102
        return self._bot_instance.row if self._bot_instance else 0
