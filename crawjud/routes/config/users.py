"""Module for Admin configuration routes."""

from __future__ import annotations

from traceback import format_exception
from typing import TYPE_CHECKING

from quart import (
    Response,
    abort,
    jsonify,
    make_response,
    request,
)
from quart import current_app as app
from quart_jwt_extended import get_jwt_identity, jwt_required

from crawjud.models import LicensesUsers, Users
from crawjud.models import SuperUser as SuperUser

from . import admin

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


def license_(usr: int) -> LicensesUsers | None:
    """Get the user's license.

    Returns:
        LicensesUsers | None: License of the user or None if not found.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    return (
        db.session.query(LicensesUsers)
        .select_from(Users)
        .join(Users, LicensesUsers.user)
        .filter(Users.id == usr)
        .first()
    )


class DeleteError(Exception):
    """Exception raised when trying to delete the user itself."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        self.message = message


class UpdateError(Exception):
    """Exception raised when trying to update the user itself."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        self.message = message


class InsertError(Exception):
    """Exception raised when trying to insert the user itself."""

    def __init__(self, message: str) -> None:
        """Initialize the exception."""
        self.message = message


def cadastro_user(form: dict) -> None:
    """User registration.

    Args:
        form (dict): user info.

    Raises:
        InsertError: If the user tries to insert itself.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        password = form.pop("password")

        usr = Users(**form)
        usr.senhacrip = password
        usr.licenseusr = license_(get_jwt_identity())

        db.session.add(usr)
        db.session.commit()

    except ValueError as e:
        raise InsertError(message=f"Erro ao inserir usuário: {e!s}") from e


def update_user(form: dict) -> None:
    """Update user.

    Args:
        form (dict): user info.

    Raises:
        UpdateError: If the user tries to update itself.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        password: str = form.pop("password")

        usr = db.session.query(Users).filter(Users.id == form["id"]).first()

        if password:
            usr.senhacrip = str(password)

        db.session.commit()
    except ValueError as e:
        raise UpdateError(message=f"Erro ao atualizar usuário: {e!s}") from e


def delete_user(form: dict) -> None:
    """Delete user.

    Args:
        form (dict): user info.\

    Raises:
        DeleteError: If the user tries to delete itself.

    """
    db: SQLAlchemy = app.extensions["sqlalchemy"]

    usr = db.session.query(Users).filter(Users.id == form["id"]).first()

    if usr.id == get_jwt_identity():
        raise DeleteError(message="Não é possível deletar seu próprio usuário.")
    db.session.delete(usr)
    db.session.commit()


action = {"INSERT": cadastro_user, "UPDATE": update_user, "DELETE": delete_user}


@admin.get("/users")
@jwt_required
async def users() -> Response:
    """Render the users list template.

    Returns:
        Response: HTTP response with rendered template.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        if request.method == "POST":
            try:
                form_data = (
                    await request.json or await request.data or await request.form
                )

                form = {}
                form.update(form_data)

                method_request: str = form.pop("method_request")
                action.get(method_request)(form)

                message = "Salvo com sucesso!"
                if method_request == "DELETE":
                    message = "Deletado com sucesso!"

                return await make_response(jsonify(message=message), 200)
            except (InsertError, UpdateError, DeleteError) as e:
                return await make_response(jsonify({"message": str(e)}, 400))

        if request.method == "GET":
            user_id: int = get_jwt_identity()
            user = db.session.query(Users).filter(Users.id == user_id).first()

            if not user.supersu or not user.admin:
                abort(403, description="Acesso negado")

            data = []

            database = (
                db.session.query(Users)
                .join(LicensesUsers)
                .filter_by(license_token=user.licenseusr.license_token)
            )

            for item in database:
                item_data = {
                    "id": item.id,
                    "login": item.login,
                    "nome_usuario": item.nome_usuario,
                    "email": item.email,
                }

                data.append(item_data)

            return await make_response(jsonify(database=data))

    except ValueError as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description="Erro interno do servidor")
