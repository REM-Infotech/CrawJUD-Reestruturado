"""
Module for credentials routes.

This module defines endpoints for listing, creating, editing, and deleting credentials.
"""

from pathlib import Path
from traceback import format_exception
from typing import TypedDict

import aiofiles
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    abort,
    current_app,
    json,
    jsonify,
    make_response,
    request,
    session,
)
from quart import current_app as app
from quart.datastructures import FileStorage
from quart_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.datastructures import MultiDict
from werkzeug.utils import secure_filename

from api import db
from api.interface.credentials import CredendialsDict
from api.interface.session import SessionDict
from api.models import BotsCrawJUD, Credentials, LicensesUsers, Users

cred = Blueprint("creds", __name__)


class CredentialsForm(TypedDict):
    """
    CredentialsForm is a data container for managing authentication credentials.

    It stores details such as the credential name, associated system, authentication method, and optional fields like
    login and certificate information.

    Attributes:
        nome_cred (str): The unique name or identifier for the credentials.
        system (str): The specific system with which the credentials are associated.
        auth_method (str): The method of authentication (e.g., basic, certificate-based).
        login (Optional[str]): The username for login if applicable; otherwise, None.
        password (Optional[str]): The password corresponding to the login; otherwise, None.
        cert (Optional[FileStorage]): The certificate file as a FileStorage instance if required; otherwise, None.
        key (Optional[str]): The key associated with the certificate if applicable; otherwise, None.

    """

    doc_cert: str
    nome_cred: str
    system: str
    auth_method: str
    login: str
    password: str
    cert: FileStorage
    key: str


async def license_user(usr: int, db: SQLAlchemy) -> str:
    """
    Return license token.

    Args:
        usr (int): User ID.
        db (SQLAlchemy): Database session.

    Returns:
        str: License token associated with the user.



    """
    query = (
        db.session.query(LicensesUsers)
        .select_from(Users)
        .join(Users, LicensesUsers.user)
        .filter(Users.id == usr)
        .first()
    )

    return query.license_token


@cred.get("/systems")
@jwt_required
async def systems() -> Response:
    """
    Return array list systems.

    Returns:
        Response: JSON response containing a list of systems.


    """
    list_systems: list[dict[str, str]] = [
        {"value": None, "text": "Escolha um sistema", "disabled": True}
    ]

    for item in db.session.query(BotsCrawJUD).all():
        if item.system not in [i["text"] for i in list_systems]:
            list_systems.append({"value": item.id, "text": item.system})
        else:
            continue
    return await make_response(
        jsonify(systems=list_systems),
        200,
    )


@cred.route("/credentials", methods=["GET", "POST"])
@jwt_required
async def credentials() -> Response:
    """
    Display a list of credentials.

    Returns:
        Response: A Quart response containing the list of credentials in JSON format.

    """
    try:
        sess = SessionDict(**{
            k: v for k, v in list(session.items()) if not k.startswith("_")
        })
        license_user = sess["license_object"]
        license_token = license_user["license_token"]
        query = (
            db.session.query(Credentials)
            .select_from(LicensesUsers)
            .join(Credentials.license_usr)
            .filter(LicensesUsers.license_token == license_token)
            .all()
        )

        credentials: list[CredendialsDict] = []

        for item in query:
            loginmethod = (
                "Usuário/Senha"
                if item.login_method == "pw"
                else "Certificado difital"
            )
            credentials.append(
                CredendialsDict(
                    id=item.id,
                    nome_credencial=item.nome_credencial,
                    system=item.system,
                    login_method=loginmethod,
                )
            )

        return await make_response(jsonify(database=credentials), 200)

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)


@cred.route("/peform_credencial", methods=["POST", "DELETE"])
@jwt_required
async def cadastro() -> Response:
    """
    Handle the creation of new credentials.

    Returns:
        Response: A Quart response after processing the credentials form.

    """
    try:
        request_data: MultiDict = (
            await request.form or await request.data or await request.json
        )

        if isinstance(request_data, bytes):
            request_data = request_data.decode()
            if isinstance(request_data, str):
                request_data = json.loads(request_data)

        action_ = request_data.get("action")

        if action_ and action_.upper() == "DELETE":
            cred_id = request_data.get("id")
            db.session.query(Credentials).filter(Credentials.id == cred_id).delete()
            db.session.commit()
            return await make_response(
                jsonify(message="Credencial deletada com sucesso!"), 200
            )

        form = CredentialsForm(**request_data)

        async def pw(form: CredentialsForm) -> None:
            form["system"] = (
                db.session.query(BotsCrawJUD)
                .filter(BotsCrawJUD.system == form["system"])
                .first()
                .system
            )
            passwd = Credentials(
                nome_credencial=form["nome_cred"],
                system=form["system"],
                login_method=form["auth_method"],
                login=form["login"],
                password=form["password"],
            )
            licenseusr = LicensesUsers.query.filter(
                LicensesUsers.license_token
                == await license_user(get_jwt_identity(), db),
            ).first()

            passwd.license_usr = licenseusr
            db.session.add(passwd)
            db.session.commit()

        async def cert(form: CredentialsForm) -> None:
            form["system"] = (
                db.session.query(BotsCrawJUD)
                .filter(BotsCrawJUD.id == form["system"])
                .first()
                .system
            )
            temporarypath = current_app.config["TEMP_DIR"]
            filecert = form["cert"]

            cer_path = str(
                Path(temporarypath)
                .resolve()
                .joinpath(secure_filename(filecert.filename))
            )

            await filecert.save(cer_path)

            async with aiofiles.open(cer_path, "rb") as f:
                certficate_blob = f.read()

                passwd = Credentials(
                    nome_credencial=form["nome_cred"],
                    system=form["system"],
                    login_method=form["auth_method"],
                    login=form["doc_cert"],
                    key=form["key"],
                    certficate=secure_filename(filecert.filename),
                    certficate_blob=await certficate_blob,
                )
                licenseusr = LicensesUsers.query.filter(
                    LicensesUsers.license_token
                    == await license_user(get_jwt_identity(), db),
                ).first()

                passwd.license_usr = licenseusr

                db.session.add(passwd)
                db.session.commit()

        callables = {"cert": cert, "pw": pw}

        await callables[form["auth_method"]](form)

        return await make_response(jsonify(message="Credencial salva com sucesso!"))

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)
