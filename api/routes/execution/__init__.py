"""
Module for execution routes.

This module provides endpoints for listing executions and downloading execution files.
"""

from __future__ import annotations

from importlib import import_module
from traceback import format_exception
from typing import TYPE_CHECKING

from quart import (
    Blueprint,
    Response,
    abort,
    jsonify,
    make_response,
    render_template,
)
from quart import current_app as app
from quart_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)

from api import db
from api.models import Executions, Users
from api.models import SuperUser as SuperUser
from api.models import admins as admins
from crawjud.misc import generate_signed_url

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy

exe = Blueprint("exe", __name__)


@exe.route("/executions", methods=["GET", "POST"])
@jwt_required
async def executions() -> Response:
    """
    Display a list of executions filtered by search criteria.

    Returns:
        Response: A Quart response rendering the executions page.

    """
    try:
        current_user = get_jwt_identity()

        executions = db.session.query(Executions).all()
        user = db.session.query(Users).filter(Users.id == current_user).first()

        if not user.supersu:
            executions = list(
                filter(lambda x: str(x.license_usr.license_token) == str(user.licenseusr.license_token), executions),
            )

            if not user.admin:
                executions = list(filter(lambda x: x.user.id == current_user, executions))

        data = [
            {
                "pid": item.pid,
                "user": item.user.nome_usuario,
                "botname": item.bot.display_name,
                "xlsx": item.arquivo_xlsx,
                "start_date": item.data_execucao,
                "status": item.status,
                "stop_date": item.data_finalizacao,
                "file_output": item.file_output,
            }
            for item in executions
        ]

        return jsonify(data=data)

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)


@exe.route("/executions/download/<filename>")
@jwt_required
async def download_file(filename: str) -> Response:
    """
    Generate a signed URL and redirect to the file download.

    Args:
        filename (str): The name of the file to download.

    Returns:
        Response: A Quart redirect response to the signed URL.

    """
    signed_url = generate_signed_url(filename)

    # Redireciona para a URL assinada
    return await make_response(jsonify(url=signed_url))


def schedule_route() -> None:
    """Import the schedules module and add the route to the Quart application."""
    import_module(".schedules", __package__)


schedule_route()


@exe.post("/clear_executions")
@jwt_required
async def clear_executions() -> Response:
    """
    Clear all executions from the database.

    Returns:
        Response: A Quart response indicating the result of the operation.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        db.session.query(Executions).filter(Executions.status == "Finalizado").delete()
        db.session.commit()

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)

    message = "Execuções removidas com sucesso!"
    template = "include/show.html"
    return await make_response(
        await render_template(
            template,
            message=message,
        ),
    )
