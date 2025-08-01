"""Módulo de gerenciamento da inicialização dos bots."""

from __future__ import annotations

import json  # noqa: F401
import traceback
from os import path
from pathlib import Path
from traceback import format_exception  # noqa: F401
from typing import TYPE_CHECKING, Any, List, Self, TypedDict
from uuid import uuid4

import aiofiles
import chardet
from celery import Celery
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
from werkzeug.datastructures import MultiDict
from werkzeug.utils import secure_filename

from addons.storage import Storage
from api.addons.make_models import MakeModels  # noqa: F401
from api.interface.formbot import FormDict  # noqa: F401
from api.interface.session import SessionDict
from api.models import BotsCrawJUD  # noqa: F401
from api.models.bots import Credentials  # noqa: F401
from api.models.users import LicensesUsers, Users  # noqa: F401

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


workdir = Path(__file__).cwd()


class FormData(TypedDict):  # noqa: D101
    @classmethod
    async def _form_data(cls) -> MultiDict:
        data = await request.data or await request.form or await request.json
        if isinstance(data, bytes):
            data = data.decode()
            if isinstance(data, str):
                data = json.loads(data)

        return data

    @classmethod
    async def constructor(cls) -> Self:  # noqa: D102
        files = await request.files
        data = await cls._form_data()

        _data = {}

        for k, v in list(data.items()):
            _data.update({k: v})

        for k, v in list(files.items()):
            _data.update({k: v})

        return cls(**_data)


class LoadForm:  # noqa: D101
    db: SQLAlchemy
    credentials: List[Credentials]
    bots: List[BotsCrawJUD]
    bot: BotsCrawJUD
    license_user: LicensesUsers
    sid: str
    upload_folder: Path
    pid: str
    sess: SessionDict

    def __init__(self) -> None:  # noqa: D107
        sess = SessionDict(**dict(list(session.items())))

        self.db = current_app.extensions["sqlalchemy"]
        license_user = self._license_user(sess)
        sid = getattr(session, "sid", None)
        if not sid:
            abort(500)

        if not license_user:
            abort(500)

        self.sess = sess
        self.license_user = license_user
        self.sid = sid
        self.bots = license_user.bots
        self.credentials = license_user.credentials
        self.upload_folder = workdir.joinpath("temp", self.sid.upper())

    async def loadform(  # noqa: D102, D103
        self,
    ) -> str:
        try:
            data = await FormData.constructor()
            self.bot = await self._query_bot(int(data["bot_id"]))
            form_data = await self._update_form_data(data)
            form = await FormDict.constructor(bot=self.bot, data=form_data)

            form["email_subject"] = self.sess["current_user"]["email"]
            form["user_name"] = self.sess["current_user"]["nome_usuario"]
            form["user_id"] = self.sess["current_user"]["id"]

            name_file_config, json_config = await self._files_task_kwargs(form)

            celery_app: Celery = current_app.extensions["celery"]

            args_task = {
                "name": self.bot.type.lower(),
                "system": self.bot.system.lower(),
                "file_config": json_config,
                "config_folder_name": name_file_config,
            }

            _task = celery_app.send_task("run_bot", kwargs=args_task, countdown=1)

            return _task.task_id

        except Exception as e:
            current_app.logger.error("\n".join(traceback.format_exception(e)))
            abort(500)

    def _license_user(self, sess: SessionDict) -> LicensesUsers | None:
        try:
            return (
                self.db.session.query(LicensesUsers)
                .filter(
                    LicensesUsers.license_token
                    == sess["license_object"]["license_token"]
                )
                .first()
            )
        except KeyError:
            abort(401)

    async def _get_annotations(self) -> dict[str, Any]:
        return FormDict.get_annotations(
            self.bot.classification.upper(), self.bot.form_cfg
        )

    async def _files_task_kwargs(self, data: FormDict) -> tuple[str, str]:
        name_file_config = self.sid.upper()
        json_file = self.upload_folder.joinpath(name_file_config).with_suffix(".json")

        data.update({json_file.name: json_file.name})

        async with aiofiles.open(json_file, "wb") as f:
            await f.write(bytes(json.dumps(data), encoding="utf-8"))

        storage = Storage("minio")
        sid = getattr(session, "sid", None)
        _sid = sid if sid else uuid4().hex

        path_minio = path.join(_sid.upper(), json_file.name)
        await storage.upload_file(path_minio, json_file)

        return name_file_config, json_file.name

    async def _update_form_data(self, _data: FormData) -> None:
        form_data = {}

        class_items = await self._get_annotations()
        for item in list(class_items.keys()):
            val = _data.get(item)
            if val:
                if item == "creds":
                    credential = await self._query_credentials(int(val))
                    form_data.update(await self._format_credential(credential))
                    continue

                form_data.update({item: secure_filename(val)})

        return form_data

    async def _query_bot(self, bot_id: int) -> BotsCrawJUD:
        bot_filter = list(filter(lambda x: x.id == bot_id, self.bots))
        return bot_filter[-1] if len(bot_filter) > 0 else abort(500)

    async def _query_credentials(self, credential_id: int) -> Credentials:
        filtered_creds = list(
            filter(lambda x: x.id == credential_id, self.credentials)
        )
        return filtered_creds[-1] if len(filtered_creds) > 0 else abort(500)

    async def _detect_encoding(self, data: bytes) -> str:  # noqa: D103
        get_encode = chardet.detect(data)
        encode = get_encode.get("encoding", "utf-8")

        return encode if encode else "utf-8"

    async def _format_credential(self, query: Credentials) -> dict[str, str]:
        val = {}
        if query.login_method == "pw":
            val = {"username": query.login, "password": query.password}

        elif query.login_method == "cert":
            val = {
                "cert": query.certficate,
                "key_cert": query.key,
            }

        return val
