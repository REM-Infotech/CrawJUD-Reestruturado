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

import shutil
import traceback
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING, Any, AnyStr, Literal, Self

from celery import Task
from pytz import timezone

from addons.printlogs._interface import MessageLog
from addons.storage import Storage
from celery_app import app
from celery_app._wrapper import shared_task

if TYPE_CHECKING:
    from common.bot import ClassBot
    from crawjud.core import CrawJUD

workdir = Path(__file__).cwd()

TypeLog = Literal["log", "success", "warning", "info", "error"]
StatusType = Literal["Inicializando", "Em Execução", "Finalizado", "Falha"]


class BotTask:  # noqa: D101
    _total_rows: int = 0
    _master_instance: CrawJUD = None
    count_id_log: int = 0
    current_task: Task = None
    start_time: datetime = None
    _pid: str = ""
    __name__ = "BotTask"
    __annotations__ = {"name": str, "system": str}

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
            self.pid = pid

            module_name = f"crawjud.bots.{system.lower()}.{name.lower()}"
            bot = import_module(module_name, __package__)
            class_bot: type[ClassBot] = getattr(bot, name.capitalize(), None)
            self.master_instance = class_bot()
            self.master_instance.print_msg = self.print_msg

            # Aguarda a finalização da task de upload antes de continuar
            path_config = await self.download_files(pid, config_folder_name)

            await self.master_instance.initialize(
                pid=pid,
                task_bot=self,
                bot_name=name,
                bot_system=system,
                path_config=path_config,
            )

            return await self.master_instance.execution()

        except Exception as e:
            _msg = "\n".join(traceback.format_exception(e))
            print(_msg)
            raise e

    @property
    def pid(self) -> str:  # noqa: D102
        return self._pid

    @pid.setter
    def pid(self, new_val: str) -> None:
        self._pid = new_val

    def print_msg(  # noqa: D102
        self,
        message: str = "Carregando",
        pid: str = None,
        row: int = 0,
        type_log: str = "log",
        status: str = "Inicializando",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        pid = pid if pid else str(self.pid)
        total_count = self.master_instance.total_rows
        time_exec = datetime.now(tz=timezone("America/Manaus")).strftime("%H:%M:%S")
        prompt = f"[({pid[:6].upper()}, {type_log}, {row}, {time_exec})> {message}]"

        data = MessageLog(
            message=prompt,
            pid=str(self.pid),
            row=row,
            type=type_log,
            status=status,
            total=total_count,
            success=0,
            errors=0,
            remaining=self.master_instance.total_rows,
            start_time=self.start_time.strftime("%d/%m/%Y, %H:%M:%S"),
        )
        app.send_task(
            "print_message",
            kwargs={
                "data": data,
                "room": str(pid),
                "event": "log_execution",
            },
        )

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
        path_files = workdir.joinpath("temp", pid)

        await storage.download_files(
            dest=path_files,
            prefix=config_folder_name,
        )

        for root, _, files in path_files.joinpath(config_folder_name).walk():
            for file in files:
                shutil.move(root.joinpath(file), path_files.joinpath(file))

        shutil.rmtree(path_files.joinpath(config_folder_name))

        return path_files.joinpath(f"{config_folder_name}.json")
