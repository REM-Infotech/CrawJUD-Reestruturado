"""Module for bot operation routes."""

from __future__ import annotations

import json  # noqa: F401
from traceback import format_exception  # noqa: F401
from typing import TYPE_CHECKING, Union

from quart import (
    Blueprint,
    Response,  # noqa: F401
    abort,
    current_app,  # noqa: F401
    jsonify,  # noqa: F401
    make_response,  # noqa: F401
    render_template,  # noqa: F401
    request,  # noqa: F401
    session,  # noqa: F401
)
from quart import current_app as app  # noqa: F401
from quart_jwt_extended import get_jwt_identity, jwt_required  # noqa: F401

from api.addons import generate_pid
from api.addons.make_models import MakeModels  # noqa: F401
from api.interface.formbot.administrativo import (
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
)
from api.interface.formbot.juridico import (
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormProcParte,
)
from api.interface.session import SessionDict
from api.models import BotsCrawJUD  # noqa: F401
from api.models.bots import Credentials  # noqa: F401
from api.models.users import LicensesUsers  # noqa: F401
from api.routes.bot.botlaunch_methods import license_user  # noqa: F401

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy  # noqa: F401


bot = Blueprint("bot", __name__, url_prefix="/bot")

class_form_dict = Union[
    JuridicoFormFileAuth,
    JuridicoFormMultipleFiles,
    JuridicoFormOnlyAuth,
    JuridicoFormOnlyFile,
    JuridicoFormPautas,
    JuridicoFormProcParte,
    AdministrativoFormFileAuth,
    AdministrativoFormMultipleFiles,
]

FORM_CONFIG: dict[str, dict[str, class_form_dict]] = {
    "JURIDICO": {
        "only_auth": JuridicoFormOnlyAuth,
        "file_auth": JuridicoFormFileAuth,
        "multipe_files": JuridicoFormMultipleFiles,
        "only_file": JuridicoFormOnlyFile,
        "pautas": JuridicoFormPautas,
        "proc_parte": JuridicoFormProcParte,
    },
    "ADMINISTRATIVO": {
        "file_auth": AdministrativoFormFileAuth,
        "multipe_files": AdministrativoFormMultipleFiles,
    },
}


async def loadform() -> class_form_dict:  # noqa: D103
    db: SQLAlchemy = current_app.extensions["sqlalchemy"]
    data = await request.data or await request.form or await request.json
    files = await request.files
    sess = SessionDict(**dict(list(session.items())))
    if isinstance(data, bytes):
        data = data.decode()
        if isinstance(data, str):
            data = json.loads(data)

    query = (
        db.session.query(BotsCrawJUD)
        .filter(BotsCrawJUD.id == data.get("bot_id"))
        .first()
    )
    if not query:
        abort(500)

    _data = dict(list(data.items()))
    _data.update(dict(list(files.items())))

    class_bot_form = FORM_CONFIG.get(query.classification.upper()).get(
        query.form_cfg.lower()
    )

    form_data = {}

    for item in list(class_bot_form.__annotations__.keys()):
        val = _data.get(item)
        if val:
            if item == "creds":
                val = (
                    db.session.query(Credentials)
                    .select_from(LicensesUsers)
                    .join(Credentials.license_usr)
                    .filter(
                        LicensesUsers.license_token
                        == sess["license_object"]["license_token"]
                    )
                    .filter(Credentials.id == val)
                    .first()
                )
                if not val:
                    abort(500)
            form_data.update({item: val})

    return class_bot_form(**form_data)


@jwt_required
@bot.get("/get_form")
async def get_form() -> Response:  # noqa: D103
    return await make_response(jsonify(config="ok"))


@jwt_required
@bot.post("/start_bot")
async def start_bot() -> None:  # noqa: D103
    pid = generate_pid()
    classDict = await loadform()  # noqa: F841, N806
    return await make_response(jsonify(message="Execução iniciada!", pid=pid))
