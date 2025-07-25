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

from os import environ
from pathlib import Path
from typing import TYPE_CHECKING

from socketio import AsyncSimpleClient

from celery_app._wrapper import shared_task

if TYPE_CHECKING:
    pass

workdir_path = Path(__file__).cwd()

server = environ.get("SOCKETIO_SERVER_URL", "http://localhost:5000")
namespace = environ.get("SOCKETIO_SERVER_NAMESPACE", "/")

transports = ["websocket"]
headers = {"Content-Type": "application/json"}
url_server = environ["SOCKETIO_SERVER_URL"]


@shared_task(name="print_message")
async def print_message(  # noqa: D103
    event: str,
    data: dict[str, str] | str,
    room: str = None,
) -> None:
    async with AsyncSimpleClient(
        reconnection_attempts=20,
        reconnection_delay=5,
    ) as sio:
        await sio.connect(
            url=server, namespace=namespace, headers=headers, transports=transports
        )

        if room:
            join_data = {"data": {"room": room}}
            await sio.emit("join_room", data=join_data)

        await sio.emit(event, data={"data": data})
