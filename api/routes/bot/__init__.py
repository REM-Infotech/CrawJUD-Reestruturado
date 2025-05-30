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


bot = Blueprint("bot", __name__)
