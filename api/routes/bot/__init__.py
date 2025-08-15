"""Module for bot operation routes."""

from __future__ import annotations

import traceback

from quart import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
)
from quart_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException

from api.routes.bot.botlaunch_methods import LoadForm
from crawjud.decorators.api import crossdomain
from crawjud.utils.xlsx_generator import MakeTemplates as MakeTemplates

bot = Blueprint("bot", __name__, url_prefix="/bot")


@bot.route("/start_bot", methods=["get", "post", "options"])
@crossdomain(origin="*", methods=["get", "post", "options"])
@jwt_required
async def start_bot() -> None:  # noqa: D103
    try:
        pid = await LoadForm().loadform()

        return await make_response(jsonify(message="Execução iniciada!", pid=pid))

    except HTTPException as e:
        current_app.logger.error("\n".join(traceback.format_exception(e)))
        return await make_response(jsonify(error="erro"), 500)


@bot.errorhandler(401)
async def handle_http_exception(error: HTTPException) -> Response:
    """Handle HTTP exceptions and render a custom error page.

    Args:
        error (HTTPException): The raised HTTP exception.

    Returns:
        tuple: A tuple containing the rendered error page and the HTTP status code.

    """
    name = error.name
    desc = error.description

    return await make_response(jsonify(name=name, description=desc), error.code)
