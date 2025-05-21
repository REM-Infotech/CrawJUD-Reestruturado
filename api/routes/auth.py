"""Module for authentication routes.

This module defines the authentication-related routes for the API, including
    user login, logout, and token refresh functionality.
    It utilizes Quart for asynchronous HTTP handling and quart_jwt_extended for
    JWT-based authentication. The module provides endpoints
    for user authentication, session management, and secure token handling.

Routes:
    /login (GET, POST, OPTIONS): Authenticates a user and issues JWT tokens.
    /logout (POST): Logs out the current user and clears JWT cookies.
    /refresh (POST): Refreshes the access token using a valid refresh token.
Classes:
    LoginForm: Dataclass representing the structure of the login form data.
Dependencies:
    - Quart
    - quart_jwt_extended
    - pytz
    - SQLAlchemy (for database access)
    - api.models.users (for user and token blocklist models)

"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from traceback import format_exception
from typing import TYPE_CHECKING

import pytz
from quart import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
)
from quart_jwt_extended import (  # noqa: F401
    create_access_token,
    create_refresh_token,
    decode_token,
    get_csrf_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from api.models.users import TokenBlocklist as TokenBlocklist
from api.models.users import Users

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


auth = Blueprint("auth", __name__)

usr = None


@dataclass
class LoginForm:
    """
    Represents the data required for user login.

    Attributes:
        login (str): The user's login identifier (e.g., username or email).
        password (str): The user's password.
        remember_me (bool): Indicates whether the user should remain logged in across sessions.

    """

    """Dataclass for the login form."""

    login: str
    password: str
    remember_me: bool


@auth.route("/login", methods=["GET", "POST", "OPTIONS"])
async def login() -> Response:
    """
    Authenticate the user and start a session.

    Returns:
        Response: HTTP response redirecting on success or rendering the login template.

    """
    try:
        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        request_json: dict[str, str] = await request.json or await request.form or await request.data
        if request.method == "OPTIONS":
            return await make_response(jsonify({"message": "OK"}), 200)

        if isinstance(request_json, bytes):
            request_json = json.loads(request_json.decode("utf-8"))

        if not request_json:
            return await make_response(jsonify({"message": "Erro ao efetuar login!"}), 400)

        username = request_json.get("login")
        password = request_json.get("password")
        remember = request_json.get("remember_me")
        form = LoginForm(username, password, remember)

        usr = db.session.query(Users).filter(Users.login == form.login).first()
        if usr and usr.check_password(form.password):
            access_token = create_access_token(identity=usr)
            refresh_token = create_refresh_token(identity=usr)

            is_admin = bool(usr.admin or usr.supersu)

            current_time = datetime.now(pytz.timezone("America/Manaus"))
            expiration_access = (current_time + timedelta(days=7)).strftime("%d-%m-%Y %H:%M:%S")
            expiration_refresh = (current_time + timedelta(days=15)).strftime("%d-%m-%Y %H:%M:%S")

            return await make_response(
                jsonify({
                    "access": {"token": access_token, "expiration": expiration_access},
                    "refresh": {"token": refresh_token, "expiration": expiration_refresh},
                    "timezone": "America/Manaus",
                    "isAdmin": is_admin,
                }),
                200,
            )

        if not usr or not usr.check_password(form.password):
            resp = jsonify({"message": "Usuário ou senha incorretos!"})
            resp.status_code = 401
            resp.headers = {"Content-Type": "application/json"}
            return resp

    except (ValueError, Exception) as e:
        current_app.logger.error("\n".join(format_exception(e)))
        return await make_response(jsonify({"message": "Erro ao efetuar login!"}))


@auth.route("/logout", methods=["POST"])
async def logout() -> Response:
    """
    Log out the current user and clear session cookies.

    Returns:
        Response: Redirect response to the login page.

    """
    response = await make_response(jsonify(msg="Logout efetuado com sucesso!"))
    try:
        unset_jwt_cookies(response)

    except (ValueError, Exception) as e:
        current_app.logger.exception("\n".join(format_exception(e)))
    return response


# Rota para atualizar o token de acesso
@auth.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
async def refresh() -> Response:
    """
    Refresh the access token.

    Returns:
        Response: JSON response with new access and refresh tokens.

    """
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    new_refresh_token = create_refresh_token(identity=current_user)

    return await make_response(jsonify(access_token=new_access_token, refresh_token=new_refresh_token), 200)
