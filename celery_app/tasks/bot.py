"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from importlib import import_module
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from celery.app import shared_task

from addons.printlogs import PrintMessage
from addons.storage import Storage
from common.bot import ClassBot

if TYPE_CHECKING:
    from celery_app.types import TReturnMessageExecutBot


@shared_task
async def initialize_bot(name: str, system: str, pid: str) -> TReturnMessageExecutBot:
    """Inicializa uma execução do robô."""
    # from celery_app import app

    # app.send_task("send_email", kwargs={})

    bot = import_module(f"crawjud.bots.{system.lower()}.{name.lower()}", __package__)

    storage = Storage("minio")
    path_files = Path(__file__).cwd().joinpath("temp")
    await storage.download_files(
        dest=path_files,
        prefix=pid,
    )
    path_config = path_files.joinpath(pid, f"{pid}.json")

    class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)

    with PrintMessage(pid=pid) as prt:
        bot_instance = class_bot.initialize(
            bot_name=name, bot_system=system, path_config=path_config, prt=prt
        )

        prt.print_msg("Execução Iniciada!", pid, 0, "log")

        prt.bot_instance = bot_instance

        namespace = environ["SOCKETIO_SERVER_NAMESPACE"]

        @prt.io.on("stop_signal", namespace=namespace)
        def stop_signal(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
            bot_instance.is_stoped = True

        bot_instance.execution()
        return "Execução encerrada com sucesso!"


@shared_task
def scheduled_initialize_bot(
    bot_name: str, bot_system: str, path_config: str
) -> TReturnMessageExecutBot:
    """Inicializa uma execução agendada do robô."""
    bot = import_module(
        f"crawjud.bots.{bot_system.lower()}.{bot_name.lower()}", __package__
    )

    class_bot = getattr(bot, bot_name.capitalize(), None)
    class_bot.initialize(
        bot_name=bot_name, bot_system=bot_system, path_config=path_config
    )
    class_bot.execution()
    return "Execução encerrada com sucesso!"
