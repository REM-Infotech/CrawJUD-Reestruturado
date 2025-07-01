"""Module for bot operation routes."""

from __future__ import annotations

import json  # noqa: F401
from traceback import format_exception  # noqa: F401
from typing import TYPE_CHECKING

from quart import (
    Blueprint,
    Response,  # noqa: F401
    abort,  # noqa: F401
    jsonify,  # noqa: F401
    make_response,  # noqa: F401
    render_template,  # noqa: F401
    request,  # noqa: F401
    send_file,  # noqa: F401
)
from quart import current_app as app  # noqa: F401
from quart_jwt_extended import get_jwt_identity, jwt_required  # noqa: F401

from api.addons import generate_pid as generate_pid
from api.addons.make_models import MakeModels  # noqa: F401
from api.models import BotsCrawJUD  # noqa: F401
from api.models.bots import Credentials  # noqa: F401
from api.models.users import LicensesUsers  # noqa: F401
from api.routes.bot.botlaunch_methods import license_user  # noqa: F401

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy  # noqa: F401


bot = Blueprint("bot", __name__, url_prefix="/bot")

FORM_CONFIGURATOR = {
    "JURIDICO": {
        "only_auth": ["creds", "state", "periodic_task", "periodic_task_group"],
        "file_auth": ["xlsx", "creds", "state", "confirm_fields", "periodic_task", "periodic_task_group"],
        "multipe_files": [
            "xlsx",
            "creds",
            "state",
            "otherfiles",
            "confirm_fields",
            "periodic_task",
            "periodic_task_group",
        ],
        "only_file": ["xlsx", "state", "confirm_fields", "periodic_task", "periodic_task_group"],
        "pautas": ["data_inicio", "data_fim", "creds", "state", "varas", "periodic_task", "periodic_task_group"],
        "proc_parte": [
            "parte_name",
            "doc_parte",
            "data_inicio",
            "data_fim",
            "polo_parte",
            "state",
            "varas",
            "creds",
            "periodic_task",
            "periodic_task_group",
        ],
    },
    "ADMINISTRATIVO": {
        "file_auth": ["xlsx", "creds", "client", "confirm_fields", "periodic_task", "periodic_task_group"],
        "multipe_files": [
            "xlsx",
            "creds",
            "client",
            "otherfiles",
            "confirm_fields",
            "periodic_task",
            "periodic_task_group",
        ],
    },
    "INTERNO": {"multipe_files": ["xlsx", "otherfiles"]},
}


@bot.get("/get_form")
async def get_form() -> Response:  # noqa: D103
    classification = request.args["classification"]
    form_cfg = request.args["form_cfg"]
    config = FORM_CONFIGURATOR[classification][form_cfg]
    return await make_response(jsonify(config=config))
