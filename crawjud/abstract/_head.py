from __future__ import annotations

from typing import TYPE_CHECKING

from crawjud.abstract._buscador import BuscadorProcesso

if TYPE_CHECKING:
    from socketio import SimpleClient

    from celery_app.custom._task import ContextTask


class HeadBot(BuscadorProcesso):
    current_task: ContextTask
    sio: SimpleClient
    _stop_bot: bool = False

    @property
    def stop_bot(self) -> bool:  # noqa: D102
        return self._stop_bot

    @stop_bot.setter
    def stop_bot(self, new_value: bool) -> None:
        self._stop_bot = new_value
