# noqa: D104
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic

from celery import chain  # noqa: F401
from dotenv import load_dotenv

from celery_app._wrapper import classmethod_shared_task, shared_task
from celery_app.custom._canvas import subtask
from celery_app.custom._task import ContextTask
from celery_app.types._celery._task import Task as Task
from common.bot import ClassBot
from crawjud._wrapper import wrap_init
from crawjud.exceptions.bot import ExecutionError
from crawjud.types.bot import MessageTimeoutAutenticacao, TReturnAuth

if TYPE_CHECKING:
    from crawjud.types import BotData, T  # noqa: F401

load_dotenv()


@wrap_init
class Capa(ClassBot):  # noqa: D101
    @staticmethod
    @shared_task(name="pje.capa")
    def pje_capa(  # noqa: D102
        current_task: ContextTask,
        *args: Generic[T],
        **kwargs: Generic[T],
    ) -> None:
        autenticar = subtask("pje.autenticador", *()).apply_async(
            kwargs={"regiao": "TRF1"}
        )

        while not autenticar.ready():
            print("Aguardando autenticação...")
        _result_auth: TReturnAuth = autenticar.result

        if isinstance(_result_auth, MessageTimeoutAutenticacao):
            raise ExecutionError(
                bot_execution_id=current_task.request.pid, message=str(_result_auth)
            )

    @classmethod
    @classmethod_shared_task(name="pje.tratamento_dados")
    def tratamento_dados(cls, *args: Any, **kwargs: Any) -> None:  # noqa: D102, N805
        print("teste!")
