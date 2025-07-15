"""Module for bot operation routes."""

from __future__ import annotations

import traceback

from celery import Celery
from quart import (
    Blueprint,
    current_app,
    jsonify,
    make_response,
)
from quart_jwt_extended import jwt_required

from api.addons import generate_pid
from api.addons.make_models import MakeModels  # noqa: F401
from api.routes.bot.botlaunch_methods import (
    LoadForm,
)

bot = Blueprint("bot", __name__, url_prefix="/bot")


@jwt_required
@bot.post("/start_bot")
async def start_bot() -> None:  # noqa: D103
    pid = generate_pid()
    try:
        args_task = await LoadForm(pid=pid).loadform()  # noqa: F841, N806

        celery_app: Celery = current_app.extensions["celery"]

        celery_app.send_task("start_bot", kwargs=args_task)

        return await make_response(jsonify(message="Execução iniciada!", pid=pid))

    except Exception as e:
        current_app.logger.error("\n".join(traceback.format_exception(e)))
        return await make_response(jsonify(error="erro"), 500)
