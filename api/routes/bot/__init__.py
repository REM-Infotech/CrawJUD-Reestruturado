"""Module for bot operation routes."""

from __future__ import annotations

import traceback
from asyncio import create_task

from quart import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
)
from quart_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException

from api.addons import generate_pid
from api.addons.make_models import MakeModels  # noqa: F401
from api.routes.bot.botlaunch_methods import (
    LoadForm,
)
from api.wrapper import crossdomain

bot = Blueprint("bot", __name__, url_prefix="/bot")


@bot.route("/start_bot", methods=["get", "post"])
@crossdomain(origin="*", methods=["get", "post"])
@jwt_required
async def start_bot() -> None:  # noqa: D103
    pid = generate_pid()
    try:
        create_task(LoadForm(pid=pid).loadform())  # noqa: F841, N806

        return await make_response(jsonify(message="Execução iniciada!", pid=pid))

    except Exception as e:
        current_app.logger.error("\n".join(traceback.format_exception(e)))
        return await make_response(jsonify(error="erro"), 500)


@bot.errorhandler(401)
async def handle_http_exception(error: HTTPException) -> Response:
    """
    Handle HTTP exceptions and render a custom error page.

    Args:
        error (HTTPException): The raised HTTP exception.

    Returns:
        tuple: A tuple containing the rendered error page and the HTTP status code.

    """
    name = error.name
    desc = error.description

    return await make_response(jsonify(name=name, description=desc), error.code)
