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
    """
    Asynchronously initializes and executes a bot instance based on the provided name, system, and process ID.

    This function dynamically imports the appropriate bot module and class, downloads necessary files from storage,
    initializes the bot with its configuration, and starts its execution. It also sets up logging and a stop signal
    handler for graceful termination.

    Args:
        name (str): The name of the bot to initialize.
        system (str): The system under which the bot is categorized.
        pid (str): The process ID associated with the bot execution.

    Returns:
        TReturnMessageExecutBot: A message indicating the result of the bot execution.

    Raises:
        ImportError: If the specified bot class cannot be found in the imported module.
        Exception: For any other errors during initialization or execution, with details printed to logs.

    """
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
            f"Bot class '{name.capitalize()}' not found in module '{bot.__name__}'"
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
    """
    Initialize and executes a bot based on the provided bot name, system, and configuration path.

    This function dynamically imports the specified bot module, retrieves the corresponding bot class,
    initializes it with the given parameters, and executes its main logic.

    Args:
        bot_name (str): The name of the bot to initialize and execute.
        bot_system (str): The system or category under which the bot is organized.
        path_config (str): The file path to the configuration required for the bot.

    Returns:
        TReturnMessageExecutBot: A message indicating the successful completion of the bot execution.

    Raises:
        ImportError: If the specified bot module cannot be imported.
        AttributeError: If the bot class does not exist in the imported module.
        Exception: Propagates any exception raised during bot initialization or execution.

    """
    bot = import_module(
        f"crawjud.bots.{bot_system.lower()}.{bot_name.lower()}", __package__
    )

    class_bot = getattr(bot, bot_name.capitalize(), None)
    class_bot.initialize(
        bot_name=bot_name, bot_system=bot_system, path_config=path_config
    )
    class_bot.execution()
    return "Execução encerrada com sucesso!"
