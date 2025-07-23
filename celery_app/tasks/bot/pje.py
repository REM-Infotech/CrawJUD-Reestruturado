"""
Defines Celery tasks for initializing and executing bot instances dynamically.

Tasks:
    - initialize_bot: Asynchronously initializes and executes a bot instance based on the provided name, system, and process ID (pid). Handles dynamic import of the bot module and class, downloads required files from storage, sets up logging, and manages stop signals via Socket.IO.
    - scheduled_initialize_bot: Synchronously initializes and executes a bot instance for scheduled tasks, using the provided bot name, system, and configuration path.

Dependencies:
    - Dynamic import of bot modules and classes.
    - Storage management for downloading required files.
    - PrintMessage for logging and communication.
    - Socket.IO for handling stop signals during bot execution.

Raises:
    - ImportError: If the specified bot class cannot be found in the dynamically imported module.
    - Exception: Catches and logs any exceptions during bot initialization or execution.

"""

from __future__ import annotations

from importlib import import_module
from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from addons.storage import Storage
from celery_app.wrapper import SharedTask

if TYPE_CHECKING:
    from celery_app.types import TReturnMessageExecutBot
    from common.bot import ClassBot


class PJeTask:  # noqa: D101
    def __init__(self) -> None:
        """Cancela a inicialização super."""

    __name__ = "PJeTask"
    __annotations__ = {"name": str, "system": str, "pid": str}

    async def initialize(  # noqa: D102
        self,
        name: str,
        system: str,
        pid: str,
    ) -> TReturnMessageExecutBot:
        bot = import_module(
            f"crawjud.bots.{system.lower()}.{name.lower()}", __package__
        )

        # Get the ClassBot from the imported module
        # Using getattr to handle cases where the class might not exist
        # This allows for more flexible bot implementations
        class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)
        if class_bot is None:
            raise ImportError(
                f"Bot class '{name.capitalize()}' not found in module '{bot.__name__}'"
            )
        from addons.printlogs._async import AsyncPrintMessage

        prt_class = await AsyncPrintMessage.constructor(pid=pid)
        async with prt_class as prt:
            prt: AsyncPrintMessage
            storage = Storage("minio")

            # Print log message indicating bot initialization
            await prt.print_msg(
                "Configurando o robô...", pid, 0, "log", "Inicializando"
            )
            path_files = Path(__file__).cwd().joinpath("temp")

            # Print log message for downloading files
            await prt.print_msg(
                "Baixando arquivos do robô...", pid, 0, "log", "Inicializando"
            )

            # Download files from storage
            await storage.download_files(
                dest=path_files,
                prefix=pid,
            )

            # Print log message indicating successful file download
            await prt.print_msg(
                "Arquivos baixados com sucesso!", pid, 0, "log", "Inicializando"
            )
            path_config = path_files.joinpath(pid, f"{pid}.json")

            # Initialize the bot instance
            bot_instance = await class_bot.initialize(
                bot_name=name, bot_system=system, path_config=path_config, prt=prt
            )

            # Set the PrintMessage instance to the bot instance
            prt.bot_instance = bot_instance
            namespace = environ["SOCKETIO_SERVER_NAMESPACE"]

            # Set up the handler for stop signal
            @prt.on("stop_signal", namespace=namespace)
            async def stop_signal(*args, **kwargs) -> None:  # noqa: ANN002, ANN003
                bot_instance.is_stoped = True

            # Print log message indicating bot execution start
            await prt.print_msg(
                "Iniciando execução do robô...", pid, 0, "log", "Inicializando"
            )

            # Start the bot execution
            await bot_instance.execution()

            return "Execução encerrada com sucesso!"


initialize_pje: PJeTask = SharedTask()(PJeTask().initialize)
