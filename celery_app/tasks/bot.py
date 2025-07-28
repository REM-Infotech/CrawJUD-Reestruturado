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

from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any, AnyStr, Literal, Self

from celery import Task

from addons.printlogs._interface import MessageLog
from addons.storage import Storage
from celery_app import app
from celery_app._wrapper import shared_task
from crawjud.core import CrawJUD

if TYPE_CHECKING:
    from common.bot import ClassBot

workdir = Path(__file__).cwd()

TypeLog = Literal["log", "success", "warning", "info", "error"]
StatusType = Literal["Inicializando", "Em Execução", "Finalizado", "Falha"]


class BotTask:  # noqa: D101
    _total_rows: int
    _master_instance: CrawJUD
    count_id_log: int = 0
    current_task: Task
    start_time: datetime

    __name__ = "BotTask"
    __annotations__ = {"name": str, "system": str}

    async def print_msg(  # noqa: D102
        self,
        message: str = "Carregando",
        pid: str = None,
        row: int = 0,
        type_log: str = "log",
        status: str = "Em Execução",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        total_count = self.master_instance.total_rows
        remaining = 0
        if row > 0:
            # Calcula o número restante de linhas
            remaining = (total_count + 1) - row

        self.count_id_log += 1
        data = MessageLog(
            id_log=self.count_id_log,
            message=message,
            pid=pid,
            row=row,
            type=type_log,
            status=status,
            total=total_count,
            success=0,
            errors=0,
            remaining=remaining,
            start_time=self.start_time,
        )
        app.send_task("print_message", data, row)

    @property
    def master_instance(self) -> CrawJUD:  # noqa: D102
        return self._master_instance

    @master_instance.setter
    def master_instance(self, new_val: CrawJUD) -> None:
        self._master_instance = new_val

    @property
    def prt(self) -> Self:  # noqa: D102
        return self

    async def download_files(self, pid: str, config_folder_name: str) -> Path:  # noqa: D102
        storage = Storage("minio")
        # Download files from storage

        path_files = workdir.joinpath("temp", pid)

        await storage.download_files(
            dest=path_files,
            prefix=config_folder_name,
        )

        # Print log message indicating successful file download
        await self.print_msg(
            "Arquivos baixados com sucesso!", pid, 0, "log", "Inicializando"
        )
        return path_files.joinpath(pid, f"{config_folder_name}.json")

    @staticmethod
    @shared_task(name="run_bot")
    async def run_bot(  # noqa: D102
        *args: AnyStr,
        **kwargs: AnyStr,
    ) -> str:
        return await BotTask().start_bot(*args, **kwargs)

    async def start_bot(  # noqa: D102
        self,
        name: str,
        system: str,
        file_config: str,
        config_folder_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            current_task: Task = kwargs.get("task")
            self.current_task = current_task
            self.start_time = datetime.strptime(
                current_task.request.eta, "%Y-%m-%dT%H:%M:%S.%f%z"
            )

            pid = str(current_task.request.id)
            module_name = f"crawjud.bots.{system.lower()}.{name.lower()}"
            bot = import_module(module_name, __package__)
            class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)

            # Aguarda a finalização da task de upload antes de continuar
            path_config = await self.download_files(pid, config_folder_name)

            instance_crawjud = CrawJUD()

            master = instance_crawjud.initialize(
                pid=pid,
                task_bot=self,
                bot_name=name,
                bot_system=system,
                path_config=path_config,
            )
            await self.print_msg(
                "Iniciando execução do robô...",
                pid,
                0,
                "log",
                "Inicializando",
            )

            return await class_bot.execution(master)

        except Exception as e:
            print(e)
            return "ok"
