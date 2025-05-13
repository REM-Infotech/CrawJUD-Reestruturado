"""
Module for log routes.

This module defines endpoints for managing logs and controlling bot executions.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import httpx as requests
from quart import (
    Response,
    flash,
    jsonify,
    make_response,
    redirect,
    request,
    session,
    url_for,
)
from quart import current_app as app
from quart_jwt_extended import jwt_required

from api import db
from api.models import Executions
from crawjud.misc import generate_signed_url

from . import logsbot

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


def stopbot(user: str, pid: str, socket: str) -> None:
    """
    Stop a bot by sending a POST request to the stop endpoint.

    Args:
        user (str): The username.
        pid (str): The process identifier.
        socket (str): The socket URL.

    """
    requests.post(url=f"{socket}/stop/{user}/{pid}", timeout=300)


@logsbot.context_processor
async def setpid_socket() -> dict[str, str | None]:
    """
    Provide 'pid' and 'socket_bot' cookie values to the template context.

    Returns:
        dict: A dictionary with 'pid' and 'socket_bot' keys.

    """
    pid = request.cookies.get("pid")
    socket_bot = request.cookies.get("socket_bot")

    return {"pid": pid, "socket_bot": socket_bot}


@logsbot.route("/stop_bot/<pid>", methods=["GET"])
@jwt_required
async def stop_bot(pid: str) -> Response:
    """
    Stop the bot execution and wait until it has finished.

    Args:
        pid (str): The process identifier.

    Returns:
        Response: A Quart redirect response to the executions page.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    socket = request.cookies.get("socket_bot")
    stopbot(session["login"], pid, f"https://{socket}")

    is_stopped = True

    while is_stopped:
        execut = db.session.query(Executions).filter(Executions.pid == pid).first()

        if str(execut.status).lower() == "finalizado":
            is_stopped = False

        asyncio.sleep(2)

    await flash("Execução encerrada", "success")
    return await make_response(
        redirect(
            url_for(
                "exe.executions",
            ),
        ),
    )


@logsbot.route("/get_execution/<pid>", methods=["GET"])
@jwt_required
async def get_execution(pid: str) -> Response:
    """
    Retrieve the execution details for a given process ID.

    Args:
        pid (str): The process ID of the execution.

    Returns:
        Response: A JSON response containing the execution details or an error message.

    """
    execution = db.session.query(Executions).filter(Executions.pid == pid).first()

    if execution and execution.status == "Finalizado":
        signed_url = generate_signed_url(execution.file_output)
        return await make_response(
            jsonify(
                {"message": "OK", "document_url": signed_url},
            ),
            200,
        )

    return await make_response(jsonify({"message": "Execution not found or not finished."}), 404)
