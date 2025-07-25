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
from pathlib import Path
from typing import TYPE_CHECKING, AnyStr, cast

from celery import Task, current_task

from addons.storage import Storage
from crawjud.core import CrawJUD

if TYPE_CHECKING:
    from common.bot import ClassBot


class BotTask:  # noqa: D101
    _total_rows: int

    __name__ = "BotTask"
    __annotations__ = {"name": str, "system": str}

    @classmethod
    async def run_task(  # noqa: D102
        cls, name: str, system: str, *args: AnyStr, **kw: AnyStr
    ) -> str:
        pid = cast(Task, current_task()).request

        module_name = f"crawjud.bots.{system.lower()}.{name.lower()}"
        bot = import_module(module_name, __package__)
        class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)

        storage = Storage("minio")

        # Print log message indicating bot initialization
        await cls.print_msg("Configurando o robô...", pid, 0, "log", "Inicializando")
        path_files = Path(__file__).cwd().joinpath("temp")

        # Print log message for downloading files
        await cls.print_msg(
            "Baixando arquivos do robô...", pid, 0, "log", "Inicializando"
        )

        # Download files from storage
        await storage.download_files(
            dest=path_files,
            prefix=pid,
        )

        # Print log message indicating successful file download
        await cls.print_msg(
            "Arquivos baixados com sucesso!", pid, 0, "log", "Inicializando"
        )
        path_config = path_files.joinpath(pid, f"{pid}.json")

        master = CrawJUD.initialize(
            bot_name=name,
            bot_system=system,
            path_config=path_config,
        )
        await cls.print_msg(
            "Iniciando execução do robô...", pid, 0, "log", "Inicializando"
        )

        return await class_bot.execution(master)
