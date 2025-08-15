"""Module for execution routes.

This module provides endpoints for listing executions and downloading execution files.
"""

from __future__ import annotations

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

from crawjud.api import db
from crawjud.models import Executions, Users
from crawjud.models import SuperUser as SuperUser
from crawjud.models import admins as admins

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy

exe = Blueprint("exe", __name__)


@exe.get("/executions")
@jwt_required
def executions() -> Response:
    """Display a list of executions filtered by search criteria.

    Returns:
        Response: A Quart response rendering the executions page.

    """
    try:
        current_user = get_jwt_identity()

        executions = db.session.query(Executions).all()
        user = db.session.query(Users).filter(Users.id == current_user).first()

        if not user.supersu:
            executions = list(
                filter(
                    lambda x: str(x.license_usr.license_token)
                    == str(user.licenseusr.license_token),
                    executions,
                ),
            )

            if not user.admin:
                executions = list(
                    filter(lambda x: x.user.id == current_user, executions),
                )

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

    except ValueError as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)


@exe.post("/clear_executions")
@jwt_required
async def clear_executions() -> Response:
    """Clear all executions from the database.

    Returns:
        Response: A Quart response indicating the result of the operation.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        db.session.query(Executions).filter(
            Executions.status == "Finalizado",
        ).delete()
        db.session.commit()

    except ValueError as e:
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
