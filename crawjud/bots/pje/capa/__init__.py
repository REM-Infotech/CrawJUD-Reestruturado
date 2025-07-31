# noqa: D104
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from celery import subtask
from dotenv import load_dotenv
from selenium.webdriver.common.by import By  # noqa: F401
from selenium.webdriver.support import expected_conditions as ec  # noqa: F401
from selenium.webdriver.support.wait import WebDriverWait  # noqa: F401

from celery_app._wrapper import classmethod_shared_task, wrap_init
from common.bot import ClassBot
from crawjud.bots.pje.res.buscador import buscar_processo  # noqa: F401
from crawjud.core._dictionary import BotData  # noqa: F401
from webdriver import DriverBot  # noqa: F401

if TYPE_CHECKING:
    from crawjud.core._dictionary import BotData as BotData


load_dotenv()


@wrap_init
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
