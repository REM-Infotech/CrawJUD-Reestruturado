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
from typing import TYPE_CHECKING, AnyStr, Literal, cast

from celery import Task, current_task, shared_task

from addons.storage import Storage
from celery_app import app
from crawjud.core import CrawJUD

if TYPE_CHECKING:
    from common.bot import ClassBot

workdir = Path(__file__).cwd()

TypeLog = Literal["log", "success", "warning", "info", "error"]
StatusType = Literal["Inicializando", "Em Execução", "Finalizado", "Falha"]


class BotTask:  # noqa: D101
    _total_rows: int

    __name__ = "BotTask"
    __annotations__ = {"name": str, "system": str}

    async def print_msg(  # noqa: D102
        self,
        message: str,
        row: int = 0,
        _type: TypeLog = "log",
        status: StatusType = "Inicializando",
    ) -> None:
        app.send_task()

    async def download_files(self, pid: str, *args: AnyStr, **kw: AnyStr) -> Path:  # noqa: D102
        storage = Storage("minio")
        # Download files from storage

        path_files = workdir.joinpath("temp", pid)

        await storage.download_files(
            dest=path_files,
            prefix=pid,
        )

        # Print log message indicating successful file download
        await self.print_msg(
            "Arquivos baixados com sucesso!", pid, 0, "log", "Inicializando"
        )
        return path_files.joinpath(pid, f"{pid}.json")

    @staticmethod
    @shared_task(name="run_bot")
    async def run_bot(  # noqa: D102
        *args: AnyStr,
        **kwargs: AnyStr,
    ) -> str:
        return await BotTask(*args, **kwargs)

    async def __init__(  # noqa: D107
        self, name: str, system: str, *args: AnyStr, **kw: AnyStr
    ) -> None:
        pid = cast(Task, current_task()).request
        module_name = f"crawjud.bots.{system.lower()}.{name.lower()}"
        bot = import_module(module_name, __package__)
        class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)
        path_config = await self.download_files(pid)

        master = CrawJUD.initialize(
            self,
            bot_name=name,
            bot_system=system,
            path_config=path_config,
        )
        await self.print_msg(
            "Iniciando execução do robô...", pid, 0, "log", "Inicializando"
        )

        return await class_bot.execution(master)
