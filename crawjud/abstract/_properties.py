from __future__ import annotations

from typing import TYPE_CHECKING

from celery_app.custom._canvas import subtask
from celery_app.types._celery._canvas import Signature
from celery_app.types.bot import BotData, DictFiles
from crawjud.abstract._master import AbstractClassBot

if TYPE_CHECKING:
    from socketio import SimpleClient

    from celery_app.custom._task import ContextTask


class PropertyBot(AbstractClassBot):
    current_task: ContextTask
    sio: SimpleClient
    _stop_bot: bool = False
    _folder_storage: str = None
    _xlsx_data: DictFiles = None
    _downloaded_files: list[DictFiles] = None
    _bot_data: list[BotData] = None
    _posicoes_processos: dict[str, int] = None

    @property
    def cookies(self) -> dict[str, str]:
        return self._cookies

    @property
    def headers(self) -> dict[str, str]:
        return self._headers

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def posicoes_processos(self) -> dict[str, int]:
        return self._posicoes_processos

    @property
    def stop_bot(self) -> bool:  # noqa: D102
        return self._stop_bot

    @stop_bot.setter
    def stop_bot(self, new_value: bool) -> None:
        self._stop_bot = new_value

    @property
    def pid(self) -> str:
        return self._pid

    @pid.setter
    def pid(self, new_pid: str) -> None:
        self._pid = new_pid

    @property
    def start_time(self) -> str:
        return self._start_time

    @start_time.setter
    def start_time(self, _start_time: str) -> None:
        self._start_time = _start_time

    @property
    def total_rows(self) -> int:
        return self._total_rows

    @total_rows.setter
    def total_rows(self, _total_rows: int) -> None:
        self._total_rows = _total_rows

    @property
    def downloaded_files(self) -> list[DictFiles]:
        return self._downloaded_files

    @property
    def xlsx_data(self) -> DictFiles:
        return self._xlsx_data

    @property
    def folder_storage(self) -> str:
        return self._folder_storage

    @folder_storage.setter
    def folder_storage(self, _folder_storage: str) -> None:
        self._folder_storage = _folder_storage

    @property
    def crawjud_dataframe(self) -> Signature:
        return subtask("crawjud.dataFrame")

    @property
    def bot_data(self) -> list[BotData]:
        return self._bot_data
