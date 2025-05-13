"""
Module for credentials routes.

This module defines endpoints for listing, creating, editing, and deleting credentials.
"""

from pathlib import Path
from traceback import format_exception

import aiofiles
from flask import abort
from flask_sqlalchemy import SQLAlchemy
from quart import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    make_response,
    request,
)
from quart import current_app as app
from quart.datastructures import FileStorage
from quart_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.utils import secure_filename

from api import db
from api.models import BotsCrawJUD, Credentials, LicensesUsers, Users

cred = Blueprint("creds", __name__)


class CredentialsForm:
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

    nome_cred: str
    system: str
    auth_method: str
    login: str
    password: str
    cert: FileStorage
    key: str

    def __init__(
        self,
        nome_cred: str,
        system: str,
        auth_method: str,
        login: str = None,
        password: str = None,
        cert: FileStorage = None,
        key: str = None,
    ) -> None:
        """
        Initialize a CredentialsForm instance.

        Args:
            nome_cred (str): The unique name or identifier for the credentials.
            system (str): The system associated with the credentials.
            auth_method (str): The authentication method for the credentials.
            login (Optional[str]): The login username if applicable.
            password (Optional[str]): The login password if applicable.
            cert (Optional[FileStorage]): The certificate file for authentication, if required.
            key (Optional[str]): The key associated with the certificate, if applicable.

        """
        self.nome_cred = nome_cred
        self.system = system
        self.auth_method = auth_method
        self.login = login
        self.password = password
        self.cert = cert
        self.key = key


async def license_user(usr: int, db: SQLAlchemy) -> str:
    """
    Return license token.

    Args:
        usr (int): User ID.
        db (SQLAlchemy): Database session.

    Returns:
        str: License token associated with the user.



    """
    return (
        db.session.query(LicensesUsers)
        .select_from(Users)
        .join(Users, LicensesUsers.user)
        .filter(Users.id == usr)
        .first()
        .license_token
    )


@cred.get("/systems")
@jwt_required
async def systems() -> Response:
    """
    Return array list systems.

    Returns:
        Response: JSON response containing a list of systems.


    """
    list_systems: list[dict[str, str]] = [{"value": None, "text": "Escolha um sistema", "disabled": True}]

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
        current_user = get_jwt_identity()

        user = db.session.query(Users).filter(Users.id == current_user).first()
        database = db.session.query(Credentials).all()
        if not user.supersu:
            token = user.licenseusr.license_token
            database = db.session.query(Credentials).join(LicensesUsers).filter_by(license_token=token).all()

        cred_list = [
            {
                "id": item.id,
                "credential": item.nome_credencial,
                "system": item.system,
                "login_method": item.system,
            }
            for item in database
        ]

        return await make_response(jsonify(database=cred_list), 200)

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
        request_data: dict[str, str | None] = await request.form or await request.data or await request.json

        action_ = request_data.get("action")

        if action_ and action_.upper() == "DELETE":
            cred_id = request_data.get("id")
            db.session.query(Credentials).filter(Credentials.id == cred_id).delete()
            db.session.commit()
            return await make_response(jsonify(message="Credencial deletada com sucesso!"), 200)

        form = CredentialsForm(**request_data)

        async def pw(form: CredentialsForm) -> None:
            form.system = db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == int(form.system)).first().system

            passwd = Credentials(
                nome_credencial=form.nome_cred,
                system=form.system,
                login_method=form.auth_method,
                login=form.login,
                password=form.password,
            )
            licenseusr = LicensesUsers.query.filter(
                LicensesUsers.license_token == await license_user(get_jwt_identity(), db),
            ).first()

            passwd.license_usr = licenseusr
            db.session.add(passwd)
            db.session.commit()

        async def cert(form: CredentialsForm) -> None:
            form.system = db.session.query(BotsCrawJUD).filter(BotsCrawJUD.id == form.system).first().system
            temporarypath = current_app.config["TEMP_DIR"]
            filecert = form.cert

            cer_path = str(Path(temporarypath).resolve().joinpath(secure_filename(filecert.filename)))

            await filecert.save(cer_path)

            async with aiofiles.open(cer_path, "rb") as f:
                certficate_blob = f.read()

                passwd = Credentials(
                    nome_credencial=form.nome_cred,
                    system=form.system,
                    login_method=form.auth_method,
                    login=form.doc_cert,
                    key=form.key,
                    certficate=secure_filename(filecert.filename),
                    certficate_blob=await certficate_blob,
                )
                licenseusr = LicensesUsers.query.filter(
                    LicensesUsers.license_token == await license_user(get_jwt_identity(), db),
                ).first()

                passwd.license_usr = licenseusr

                db.session.add(passwd)
                db.session.commit()

        callables = {"cert": cert, "pw": pw}

        await callables[request_data.get("auth_method")](form)

        return await make_response(jsonify(message="Credencial salva com sucesso!"))

    except (ValueError, Exception) as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)
