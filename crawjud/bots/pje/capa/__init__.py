# noqa: D104
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dotenv import load_dotenv

from celery_app._wrapper import classmethod_shared_task
from celery_app.custom._task import ContextTask, subtask
from celery_app.types._celery import Signature
from common.bot import ClassBot
from crawjud.exceptions.bot import ExecutionError
from crawjud.types.bot import MessageTimeoutAutenticacao, TReturnAuth

if TYPE_CHECKING:
    from crawjud.types import BotData  # noqa: F401


load_dotenv()


class Capa(ClassBot):  # noqa: D101
    @classmethod
    @classmethod_shared_task(name="pje.capa")
    def pje_capa(cls, current_task: ContextTask, *args: Any, **kwargs: Any) -> None:  # noqa: D102, N805
        if isinstance(cls, str):
            cls = Capa

        cls.tratamento_dados()
        autenticar: Signature = subtask("pje.autenticador")
        _teste = autenticar.apply_async(kwargs={"regiao": "11"})
        _result_auth: TReturnAuth = _teste.get()

        if isinstance(_result_auth, MessageTimeoutAutenticacao):
            raise ExecutionError(
                bot_execution_id=current_task.request.pid, message=str(_result_auth)
            )

    @classmethod
    @classmethod_shared_task(name="pje.capa")
    def tratamento_dados(cls, *args: Any, **kwargs: Any) -> None:  # noqa: D102, N805
        print("teste!")
