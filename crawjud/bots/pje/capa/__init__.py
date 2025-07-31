# noqa: D104
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from celery import subtask
from dotenv import load_dotenv

from celery_app._wrapper import classmethod_shared_task
from celery_app._wrapper import wrap_init as wrap_init
from common.bot import ClassBot

if TYPE_CHECKING:
    from crawjud.types import BotData  # noqa: F401


load_dotenv()


class Capa(ClassBot):  # noqa: D101
    @classmethod
    @classmethod_shared_task(name="pje.capa")
    def pje_capa(cls, *args: Any, **kwargs: Any) -> None:  # noqa: D102, N805
        if isinstance(cls, str):
            cls = Capa

        cls.tratamento_dados()
        autenticar = subtask("pje.autenticador")
        _teste = autenticar.apply_async(kwargs={"regiao": "11"})

    @classmethod
    @classmethod_shared_task(name="pje.capa")
    def tratamento_dados(cls, *args: Any, **kwargs: Any) -> None:  # noqa: D102, N805
        print("teste!")
