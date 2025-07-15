"""Módulo de gerenciamento da inicialização dos bots."""

from __future__ import annotations

import json  # noqa: F401
import traceback
from pathlib import Path
from traceback import format_exception  # noqa: F401
from typing import TYPE_CHECKING, Union

import aiofiles
import chardet
import pandas as pd
from quart import (
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
from api.models.users import LicensesUsers, Users  # noqa: F401

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy

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


async def detect_encoding(data: bytes) -> str:  # noqa: D103
    get_encode = chardet.detect(data)
    encode = get_encode.get("encoding", "utf-8")

    return encode if encode else "ISO-8859-8"


async def license_user(usr: int, db: SQLAlchemy) -> str:
    """
    Return license token.

    Returns:
        str: License token of the user.

    """
    return (
        db.session.query(LicensesUsers)
        .select_from(Users)
        .join(Users, LicensesUsers.user)
        .filter(Users.id == usr)
        .first()
        .license_token
    )


async def loadform() -> class_form_dict:  # noqa: D103
    try:
        db: SQLAlchemy = current_app.extensions["sqlalchemy"]
        data = await request.data or await request.form or await request.json
        files = await request.files
        sess = SessionDict(**dict(list(session.items())))
        if isinstance(data, bytes):
            data = data.decode()
            if isinstance(data, str):
                data = json.loads(data)

        license_token = sess["license_object"]["license_token"]
        sid = getattr(session, "sid", None)

        if not sid:
            abort(500)

        query = (
            db.session.query(BotsCrawJUD)
            .select_from(LicensesUsers)
            .join(BotsCrawJUD.license)
            .filter(LicensesUsers.license_token == license_token)
            .filter(BotsCrawJUD.id == data["bot_id"])
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
                if item == "xlsx":
                    temp_folder = Path(__file__).cwd().joinpath("temp", sid, val)
                    df = pd.read_excel(temp_folder)

                    csv_path = temp_folder.with_suffix(".csv")
                    df.to_csv(csv_path)

                    async with aiofiles.open(csv_path, "r") as f:
                        blob_csv = await f.read()

                        val = {"filename": val, "blob": blob_csv}

                if item == "creds":
                    query = (
                        db.session.query(Credentials)
                        .select_from(LicensesUsers)
                        .join(Credentials.license_usr)
                        .filter(LicensesUsers.license_token == license_token)
                        .filter(Credentials.id == val)
                        .first()
                    )
                    if not query:
                        abort(500)

                    if query.login_method == "pw":
                        val = {"login": query.login, "password": query.password}

                    elif query.login_method == "cert":
                        encoding = await detect_encoding(query.certficate_blob)
                        val = {
                            "cert": query.certficate,
                            "cert_blob": query.certficate_blob.decode(encoding),
                            "key_cert": query.key,
                        }

                form_data.update({item: val})

        return class_bot_form(**form_data)
    except Exception as e:
        current_app.logger.error("\n".join(traceback.format_exception(e)))
        abort(500)


async def get_bot_info(db: SQLAlchemy, id_: int) -> BotsCrawJUD | None:
    """
    Retrieve bot information from the database.

    Returns:
        BotsCrawJUD | None: Bot information or None if not found.

    """
    return db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == id_).first()
