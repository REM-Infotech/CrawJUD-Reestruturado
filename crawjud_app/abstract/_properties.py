from __future__ import annotations

from typing import TYPE_CHECKING

from crawjud_app.abstract._master import AbstractClassBot
from crawjud_app.custom.canvas import subtask

if TYPE_CHECKING:
    from socketio import SimpleClient

    from crawjud_app.custom.task import ContextTask
    from interface.types.bot import BotData, DictFiles
    from interface.types.celery.canvas import Signature


class PropertyBot(AbstractClassBot):
    current_task: ContextTask
    sio: SimpleClient
    _stop_bot: bool = False
    _folder_storage: str | None = None
    _xlsx_data: DictFiles | None = None
    _downloaded_files: list[DictFiles] | None = None
    _bot_data: list[BotData] | None = None
    _posicoes_processos: dict[str, int] | None = None

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
    def stop_bot(self) -> bool:
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
