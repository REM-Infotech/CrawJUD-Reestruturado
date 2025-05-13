"""
Module for handling Socket.IO events for logging and managing bot executions.

This module defines event handlers used for client connections, disconnections,
log message processing, and bot control actions (stop, terminate, join, etc.).
"""

from __future__ import annotations

import asyncio
import logging
from traceback import format_exception

from socketio import AsyncServer  # noqa: F401

from api import app
from crawjud.utils import format_message_log, load_cache  # noqa: F401
from crawjud.utils.status import TaskExec
from decorators.jwt import jwt_required_socketio

logger = logging.getLogger(__name__)

# Retrieve the Socket.IO server extension from the Flask app.
io = app.extensions["socketio"]  # type: AsyncServer


@io.on("connect", namespace="/log")
@jwt_required_socketio
async def connect(
    sid: str = None,
    data: dict = None,
) -> None:
    """
    Handle a new client connection to the /log namespace.

    Args:
        sid (str): The unique session ID for the connecting client.
        data (dict): Additional connection data, expected to contain an "HTTP_PID" key.



    """
    room = data.get("HTTP_PID")
    # Join the client to a room based on the provided HTTP_PID.
    if room:
        await io.enter_room(sid, room, namespace="/log")
    # Send a welcome message to the connected client.
    await io.send("connected!", to=sid, namespace="/log")


@io.on("disconnect", namespace="/log")
@jwt_required_socketio
async def disconnect(
    sid: str = None,
    event: any = None,
    namespace: str = None,
) -> None:
    """
    Handle client disconnection from the /log namespace.

    Args:
        sid (str): The session ID of the disconnecting client.
        event (any): Additional event information (unused).
        namespace (str): The namespace from which the client is disconnecting.

    """
    await io.send("disconnected!", to=sid, namespace="/log")


@io.on("leave", namespace="/log")
@jwt_required_socketio
async def leave(
    sid: str,
    data: dict,
) -> None:
    """
    Handle a client leaving a specific logging room.

    Args:
        sid (str): The session ID of the client.
        data (dict): Data containing the key "pid" for identifying the room.

    """
    room = data["pid"]
    # Inform the client about leaving the room.
    await io.send(f"Leaving Room '{room}'", to=sid, namespace="/log")
    await io.leave_room(sid, room, "/log")


@io.on("stop_bot", namespace="/log")
@jwt_required_socketio
async def stop_bot(
    sid: str,
    data: dict[str, str],
) -> None:
    """
    Stop a running bot identified by its PID.

    Args:
        sid (str): The session ID of the client issuing the stop command.
        data (dict[str, str]): Data containing the bot's PID under the key "pid".


    """
    pid = data["pid"]
    # Trigger bot stop execution.
    await TaskExec.task_exec(data=data, exec_type="stop", app=app)
    # Notify the client that the bot was stopped.
    await io.send(
        {"message": "Bot stopped!"},
        to=sid,
        namespace="/log",
        room=pid,
    )


@io.on("terminate_bot", namespace="/log")
@jwt_required_socketio
async def terminate_bot(
    sid: str,
    data: dict[str, str],
) -> None:
    """
    Terminate a running bot identified by its PID.

    Args:
        sid (str): The session ID of the client.
        data (dict[str, str]): Data containing the bot's PID under the key "pid".

    """
    from api import db
    from api.models import ThreadBots
    from crawjud.bot import WorkerBot

    async with app.app_context():
        try:
            pid = data["pid"]
            # Retrieve process information from the database.
            process_id = db.session.query(ThreadBots).filter(ThreadBots.pid == pid).first()
            if process_id:
                process_id = str(process_id.processID)

            # Execute termination routine for the bot.
            result = await asyncio.create_task(WorkerBot.stop(process_id, pid, app))
            await io.enter_room(sid, pid, namespace="/log")
            await io.emit("log_message", result, to=sid, namespace="/log", room=pid)

        except (ValueError, Exception) as e:
            app.logger.exception("An error occurred: %s", str(e))
            await io.send("Failed to stop bot!", to=sid, namespace="/log", room=pid)


@io.on("log_message", namespace="/log")
@jwt_required_socketio
async def log_message(
    sid: str,
    data: dict[str, str] = None,
) -> None:
    """
    Process and forward incoming log messages from crawjud.bots.

    Args:
        sid (str): The session ID of the client sending the log.
        data (dict[str, str], optional): Contains the log message and PID.

    """
    async with app.app_context():
        try:
            pid = data["pid"]
            # Format the log message appropriately.
            if "message" in data:
                data = await format_message_log(data, pid, app)
                # Emit the formatted log to the specified room.
                await io.emit("log_message", data, room=pid, namespace="/log")

            await io.send("message received!", to=sid, namespace="/log", room=pid)

        except (ValueError, Exception) as e:
            err = "\n".join(format_exception(e))
            logger.exception(err)
            await io.send("failed to receive message", to=sid, namespace="/log", room=pid)


@io.on("statusbot", namespace="/log")
@jwt_required_socketio
async def statusbot(
    sid: str,
    data: dict = None,
) -> None:
    """
    Handle status updates from crawjud.bots.

    Args:
        sid (str): The session ID of the client.
        data (dict, optional): Data carrying the status and PID information.

    """
    if data:
        room = data.get("pid")
        await io.send("Bot stopped!", to=sid, namespace="/log", room=room)

    await io.send("Bot stopped!", to=sid, namespace="/log")


@io.on("join", namespace="/log")
@jwt_required_socketio
async def join(
    sid: str = None,
    data: dict[str, str] = None,
    namespace: str | None = None,
) -> None:
    """
    Handle a client joining a logging room.

    Args:
        sid (str): The session ID of the joining client.
        data (dict[str, str]): Data containing the room identifier under "pid".
        namespace (str, optional): The namespace to join.


    """
    pid = data["pid"]
    await io.enter_room(sid, pid, namespace="/log")

    # Confirm joining the room.
    await io.send(f"Joinned room! Room: {pid}", to=sid, namespace="/log")
