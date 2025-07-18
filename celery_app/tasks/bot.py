"""Modulo de gerenciamento de tarefas do Celery."""

from __future__ import annotations

from asyncio import iscoroutinefunction
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

    # Import the bot module dynamically based on the system and name
    bot = import_module(f"crawjud.bots.{system.lower()}.{name.lower()}", __package__)

    # Get the ClassBot from the imported module
    # Using getattr to handle cases where the class might not exist
    # This allows for more flexible bot implementations
    class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)
    if class_bot is None:
        raise ImportError(
            msg=f"Bot class '{name.capitalize()}' not found in module '{bot.__name__}'"
        )

    try:
        with PrintMessage(pid=pid) as prt:
            storage = Storage("minio")

            # Print log message indicating bot initialization
            prt.print_msg("Configurando o robô...", pid, 0, "log", "Inicializando")
            path_files = Path(__file__).cwd().joinpath("temp")

            # Print log message for downloading files
            prt.print_msg(
                "Baixando arquivos do robô...", pid, 0, "log", "Inicializando"
            )

            # Download files from storage
            await storage.download_files(
                dest=path_files,
                prefix=pid,
            )

            # Print log message indicating successful file download
            prt.print_msg(
                "Arquivos baixados com sucesso!", pid, 0, "log", "Inicializando"
            )
            path_config = path_files.joinpath(pid, f"{pid}.json")

            # Initialize the bot instance
            bot_instance = class_bot.initialize(
                bot_name=name, bot_system=system, path_config=path_config, prt=prt
            )

            # Set the PrintMessage instance to the bot instance
            prt.bot_instance = bot_instance
            namespace = environ["SOCKETIO_SERVER_NAMESPACE"]

            # Set up the handler for stop signal
            @prt.io.on("stop_signal", namespace=namespace)
            def stop_signal(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
                bot_instance.is_stoped = True

            # Print log message indicating bot execution start
            prt.print_msg(
                "Iniciando execução do robô...", pid, 0, "log", "Inicializando"
            )

            # Start the bot execution
            if iscoroutinefunction(bot_instance.execution):
                await bot_instance.execution()
            else:
                bot_instance.execution()
            return "Execução encerrada com sucesso!"

    except Exception as e:
        print(e)
        return "Erro no robô. Verifique os logs para mais detalhes."


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
