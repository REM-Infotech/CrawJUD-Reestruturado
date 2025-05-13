"""Module for bot operation routes."""

from __future__ import annotations

import json
import warnings
from traceback import format_exception
from typing import TYPE_CHECKING

from quart import (
    Blueprint,
    Response,
    abort,
    jsonify,
    make_response,
    render_template,
    request,
    send_file,
)
from quart import current_app as app
from quart_jwt_extended import get_jwt_identity, jwt_required

from api.addons import generate_pid
from api.addons.make_models import MakeModels
from api.models import BotsCrawJUD
from api.models.bots import Credentials
from api.models.users import LicensesUsers
from api.routes.bot.botlaunch_methods import get_bot_info, license_user, setup_task_worker
from api.routes.bot.botlaunch_methods import get_form_data as get_form_data

if TYPE_CHECKING:
    from flask_sqlalchemy import SQLAlchemy


bot = Blueprint("bot", __name__)


@bot.route("/acquire_credentials", methods=["post"])
@jwt_required
async def acquire_credentials() -> Response:
    """
    Return a list credentials.

    Returns:
        Response: JSON response containing a list of credentials.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        await_request_data = (await request.data).decode("utf-8")
        request_data = json.loads(await_request_data or "{}")
        form_data = await request.form
        request_json = await request.json
        json_data: dict[str, str] = form_data or request_json or request_data

        system = json_data["system"]
        form_cfg = json_data["form_cfg"]

        if form_cfg == "only_file":
            return jsonify({"value": "Opção não utilizada", "text": "Opção não utilizada", "disabled": True})

        cred = [{"value": None, "text": "Selecione uma credencial", "disabled": True}]

        license_token = await license_user(get_jwt_identity(), app.extensions["sqlalchemy"])

        creds = (
            db.session.query(Credentials)
            .select_from(LicensesUsers)
            .join(LicensesUsers, Credentials.license_usr)
            .filter(LicensesUsers.license_token == license_token)
            .all()
        )
        cred.extend([
            {"value": credential.nome_credencial, "text": credential.nome_credencial}
            for credential in creds
            if credential.system == system.upper()
        ])
        return jsonify(info=cred)

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        return jsonify({}, 500)


@bot.route("/acquire_systemclient", methods=["post"])
@jwt_required
async def acquire_systemclient() -> Response:
    """
    Return a list credentials.

    Returns:
        Response: JSON response containing a list of credentials.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        await_request_data = (await request.data).decode("utf-8")
        request_data = json.loads(await_request_data or "{}")
        form_data = await request.form
        request_json = await request.json
        json_data: dict[str, str] = form_data or request_json or request_data

        system = json_data["system"]
        typebot = json_data["type"]

        client = json_data["client"]
        state = json_data["state"]

        form_cfg = json_data["form_cfg"]

        if form_cfg == "only_file":
            return jsonify({"value": "Opção não utilizada", "text": "Opção não utilizada", "disabled": True})

        if state == "EVERYONE":
            type_ = "client"
            opt = [{"value": None, "text": "Selecione um cliente", "disabled": True}]

            opt.extend([
                {"value": client.client, "text": client.client}
                for client in db.session.query(BotsCrawJUD)
                .filter(
                    BotsCrawJUD.type == typebot.upper(),
                    BotsCrawJUD.system == system.upper(),
                )
                .all()
            ])
            return jsonify(info=opt, type=type_)

        if client == "EVERYONE":
            opt = [{"value": None, "text": "Selecione um Estado", "disabled": True}]
            type_ = "state"
            opt.extend([
                {"value": state.state, "text": state.state}
                for state in db.session.query(BotsCrawJUD)
                .filter(
                    BotsCrawJUD.type == typebot.upper(),
                    BotsCrawJUD.system == system.upper(),
                )
                .all()
            ])
            return jsonify(info=opt, type=type_)

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        return jsonify({}, 500)


@bot.route("/bots_list", methods=["get"])
@jwt_required
async def bots_list() -> Response:
    """
    Return a list bots.

    Returns:
        Response: JSON response containing a list of bots.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]

        bots = db.session.query(BotsCrawJUD).all()

        bots_ = [
            {
                "id": bot.id,
                "display_name": bot.display_name,
                "system": bot.system.upper(),
                "state": bot.state.upper(),
                "client": bot.client.upper(),
                "type": bot.type.upper(),
                "form_cfg": bot.form_cfg.lower(),
                "classification": bot.classification.upper(),
                "text": bot.text,
            }
            for bot in bots
        ]

        return jsonify(bots_)

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))


@bot.route("/get_model/<id_>/<system>/<typebot>/<filename>", methods=["GET"])
async def get_model(id_: int, system: str, typebot: str, filename: str) -> Response:
    """
    Retrieve a model file for the specified bot.

    Args:
        id_ (int): Bot identifier.
        system (str): System being used.
        typebot (str): Type of bot.
        filename (str): Name of the file.

    Returns:
        Response: File download response.

    """
    try:
        async with app.app_context():
            path_arquivo, nome_arquivo = MakeModels(filename, filename).make_output()
            response = await make_response(await send_file(f"{path_arquivo}", as_attachment=True))
            response.headers["Content-Disposition"] = f"attachment; filename={nome_arquivo}"
            return response

    except (ValueError, Exception) as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description=f"Erro interno. {e!s}")


@bot.route("/bot/dashboard", methods=["GET"])
@jwt_required
async def dashboard() -> Response:
    """
    Render the bot dashboard page.

    Returns:
        Response: HTTP response with rendered template.

    """
    try:
        title = "Robôs"
        page = "botboard.html"
        bots = BotsCrawJUD.query.all()

        return await make_response(await render_template("index.html", page=page, bots=bots, title=title))

    except (ValueError, Exception) as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description=f"Erro interno. {e!s}")


@bot.route("/bot/<id_>/<system>/<typebot>", methods=["POST"])
@jwt_required
async def botlaunch(id_: int, system: str, typebot: str) -> Response:
    """
    Launch the specified bot process.

    Returns:
        Response: JSON response indicating the status of the bot launch.

    """
    form = {}
    data = await request.form
    files = await request.files
    pid = generate_pid()
    try:
        form.update(data)
        form.update(files)

        periodic_bot = False

        db: SQLAlchemy = app.extensions["sqlalchemy"]
        bot_info = await get_bot_info(db, id_)
        if not bot_info:
            return await make_response(jsonify(response="Erro ao iniciar"), 500)

        display_name = bot_info.display_name
        title = display_name  # noqa: F841

        if not form:
            return await make_response(jsonify(response="ok"), 403)

        return await setup_task_worker(
            id_=id_,
            pid=pid,
            form=form,
            system=system,
            typebot=typebot,
            periodic_bot=periodic_bot,
            bot_info=bot_info,
        )

    except (ValueError, Exception) as e:
        app.logger.exception("\n".join(format_exception(e)))
        abort(500, description="Erro interno.")

    finally:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)

        except (ValueError, Exception) as e:
            app.logger.exception("\n".join(format_exception(e)))
