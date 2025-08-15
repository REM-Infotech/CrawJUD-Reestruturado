"""Module for schedule executions page."""

from __future__ import annotations

from traceback import format_exception
from typing import TYPE_CHECKING

from quart import Response, abort, make_response, render_template, session
from quart import current_app as app
from quart_jwt_extended import jwt_required
from sqlalchemy.orm import aliased

from api.models import ScheduleModel, SuperUser, Users, admins

from . import exe

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


@exe.get("/schedules")
@jwt_required
async def schedules() -> Response:
    """Display a list of executions filtered by search criteria.

    Returns:
        Response: A Quart response rendering the executions page.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        chksupersu = (
            db.session.query(SuperUser)
            .select_from(Users)
            .join(Users.supersu)
            .filter(Users.login == session["login"])
            .first()
        )

        executions = db.session.query(ScheduleModel)

        if not chksupersu:
            alias = aliased(
                Users,
                (
                    db.session.query(Users)
                    .filter(Users.login == session["login"])
                    .subquery()
                ),
            )

            executions = executions.join(
                alias,
                ScheduleModel.license_id == alias.licenseus_id,
            )

            chk_admin = (
                db.session.query(admins)
                .join(alias, admins.c.users_id == alias.id)
                .filter(admins.c.license_user_id == alias.licenseus_id)
                .first()
            )

            if not chk_admin:
                executions = executions.join(alias, ScheduleModel.user_id == alias.id)

        database = executions.all()
        title = "Execuções"
        page = "schedules.html"
        return await make_response(
            await render_template(
                "index.html",
                page=page,
                title=title,
                database=database,
            ),
        )

    except ValueError as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)


@exe.post("/delete_schedule/<int:id_>")
@jwt_required
async def delete_schedule(id_: int) -> Response:
    """Delete a schedule from the database.

    Args:
        id_ (int): The id of the schedule to be deleted.

    Returns:
        Response: A Quart response redirecting to the schedules page.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        db.session.query(ScheduleModel).filter(ScheduleModel.id == id_).delete()
        db.session.commit()
    except ValueError:
        abort(500)

    message = "Tarefa deletada!"
    template = "include/show.html"
    return await make_response(
        await render_template(
            template,
            message=message,
        ),
    )
