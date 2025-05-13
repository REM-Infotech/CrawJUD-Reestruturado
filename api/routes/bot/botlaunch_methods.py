"""Module for botlaunch route."""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Any

from quart import (
    Response,
    flash,
    jsonify,
    make_response,
    redirect,
    url_for,
)
from quart import current_app as app
from quart.datastructures import FileStorage
from quart_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename

from api.models import BotsCrawJUD, Credentials, LicensesUsers
from api.models.bots import ThreadBots
from api.models.users import Users
from crawjud.utils import makezip
from crawjud.utils.gcs_mgmt import enviar_arquivo_para_gcs
from crawjud.utils.status import TaskExec

if TYPE_CHECKING:
    from celery import Celery, Task
    from flask_sqlalchemy import SQLAlchemy

    from crawjud.types import AnyType

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


async def handle_credentials(value: str, data: dict, system: str, files: dict) -> None:
    """Handle credentials for form submission."""
    db: SQLAlchemy = app.extensions["sqlalchemy"]
    temporarypath = app.config["TEMP_DIR"]
    creds = (
        db.session.query(Credentials)
        .join(LicensesUsers)
        .filter(LicensesUsers.license_token == await license_user(get_jwt_identity(), db))
        .all()
    )
    for credential in creds:
        if all([
            credential.nome_credencial == value,
            credential.system == system.upper(),
        ]):
            if credential.login_method == "pw":
                data.update({
                    "username": credential.login,
                    "password": credential.password,
                    "login_method": credential.login_method,
                })
            elif credential.login_method == "cert":
                cert_path = Path(temporarypath).joinpath(credential.certficate)
                with cert_path.open("wb") as f:
                    f.write(credential.certficate_blob)

                content_type = mimetypes.guess_type(cert_path)
                content_lenght = cert_path.stat().st_size
                credential_object = FileStorage(
                    cert_path.open("rb"),
                    filename=credential.certficate,
                    content_type=content_type,
                    content_length=content_lenght,
                )
                files.update({credential.certficate: credential_object})
                data.update({
                    "username": credential.login,
                    "name_cert": credential.certficate,
                    "token": credential.key,
                    "login_method": credential.login_method,
                })
            break


async def get_bot_info(db: SQLAlchemy, id_: int) -> BotsCrawJUD | None:
    """
    Retrieve bot information from the database.

    Returns:
        BotsCrawJUD | None: Bot information or None if not found.

    """
    return db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == id_).first()


async def get_form_data(
    db: SQLAlchemy,
    system: str,
    typebot: str,
    bot_info: BotsCrawJUD,
) -> tuple[list[tuple], list[tuple], list[tuple[Any, Any]], list]:
    """
    Retrieve form data including states, clients, credentials, and form configuration.

    Returns:
        tuple: A tuple containing states, clients, credentials, and form configuration.

    """
    states = [
        (state.state, state.state)
        for state in BotsCrawJUD.query.filter(
            BotsCrawJUD.type == typebot.upper(),
            BotsCrawJUD.system == system.upper(),
        ).all()
    ]

    clients = [
        (client.client, client.client)
        for client in BotsCrawJUD.query.filter(
            BotsCrawJUD.type == typebot.upper(),
            BotsCrawJUD.system == system.upper(),
        ).all()
    ]

    creds = (
        db.session.query(Credentials)
        .join(LicensesUsers)
        .filter(LicensesUsers.license_token == await license_user(get_jwt_identity(), db))
        .all()
    )

    credts = [
        (credential.nome_credencial, credential.nome_credencial)
        for credential in creds
        if credential.system == system.upper()
    ]

    form_config = []
    classbot = str(bot_info.classification)
    form_setup = str(bot_info.form_cfg)

    if typebot.upper() == "PAUTA" and system.upper() == "PJE":
        form_setup = "pautas"
    elif typebot.lower() == "proc_parte":
        form_setup = "proc_parte"

    form_config.extend(FORM_CONFIGURATOR[classbot][form_setup])

    chk_typebot = typebot.upper() == "PROTOCOLO"
    chk_state = bot_info.state == "AM"
    chk_system = system.upper() == "PROJUDI"
    if all([chk_typebot, chk_state, chk_system]):
        form_config.append("password")

    return states, clients, credts, form_config


async def perform_submited_form(
    form: dict[str, str | bool | FileStorage],
    data: dict,
    files: dict,
    system: str,
    typebot: str,
    *,
    periodic_task: bool = False,
) -> tuple[dict, dict, bool]:
    """
    Perform the submitted form.

    Returns:
        tuple: A tuple containing the updated data, files, and periodic_task status.

    """
    data.update({"schedule": periodic_task})

    for key, value in form.items():
        if key == "creds":
            await handle_credentials(value, data, system, files)
            continue

        if isinstance(value, FileStorage):
            files.update({secure_filename(value.filename): value})
            if value.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                data.update({"xlsx": secure_filename(value.filename)})
            continue

        data.update({key: value})
        continue

    return data, files, periodic_task


async def setup_task_worker(
    id_: int,
    pid: str,
    form: dict,
    system: str,
    typebot: str,
    bot_info: BotsCrawJUD,
    **kwargs: AnyType,
) -> Response | None:
    """
    Send data to servers and handle the response.

    Returns:
        Response | None: The response object or None if no response is needed.

    """
    try:
        db: SQLAlchemy = app.extensions["sqlalchemy"]
        celery_app: Celery = app.extensions["celery"]
        is_started = 200
        user = db.session.query(Users).filter_by(id=get_jwt_identity()).first().login
        data: dict[str, str] = {}
        files: dict[str, FileStorage] = {}
        periodic_bot = False

        data.update({"pid": pid})

        data, files, periodic_bot = await perform_submited_form(
            form=form,
            data=data,
            files=files,
            system=system,
            typebot=typebot,
        )

        path_pid = await TaskExec.configure_path(pid=pid, files=files)
        path_args = await TaskExec.args_tojson(
            path_pid=path_pid,
            pid=pid,
            data=data,
            typebot=typebot,
        )
        execut, display_name = await TaskExec.insert_into_database(
            db=db,
            pid=pid,
            id_=id_,
            user=user,
            data=data,
            bot_info=bot_info,
        )

        kwargs_ = {
            "display_name": display_name,
            "system": system,
            "typebot": typebot,
            "path_args": str(path_args),
        }

        zip_filename, zip_file = makezip(pid)
        enviar_arquivo_para_gcs(zip_filename, zip_file, bucket_name="task_files_celery")

        if periodic_bot:
            await TaskExec.schedule_into_database(
                db=db,
                data=data,
                system=system,
                typebot=typebot,
                path_args=path_args,
                display_name=display_name,
            )

        elif not periodic_bot:
            task: Task = celery_app.send_task(f"crawjud.bot.{system.lower()}_launcher", kwargs=kwargs_)
            process_id = str(task.id)

            # Salva o ID no "banco de dados"
            add_thread = ThreadBots(pid=pid, processID=process_id)
            db.session.add(add_thread)
            db.session.commit()

        try:
            await TaskExec.send_email(
                execut=execut,
                app=app,
                type_notify="start",
                email_notify=data.get("email_notify"),
            )
        except (ValueError, Exception) as e:
            app.logger.exception("Error sending email: %s", str(e))

    except (ValueError, Exception) as e:
        app.logger.exception("Error starting bot: %s", str(e))
        is_started = 500

    if is_started == 200:
        if periodic_bot:
            await flash(message=f"Tarefa agendada com sucesso! PID: {pid}")
            return await make_response(
                redirect(
                    url_for(
                        "exe.schedules",
                        pid=pid,
                    ),
                ),
            )
        await flash(message=f"Execução iniciada com sucesso! PID: {pid}")
        return await make_response(jsonify(pid=pid), 200)

    if is_started != 200:
        await flash("Erro ao iniciar a execução!", "error")
        return await make_response(jsonify(pid=pid), 200)
    return None
