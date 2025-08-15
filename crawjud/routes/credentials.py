"""Fornece rotas relacionadas à gestão de credenciais de autenticação.

Este módulo implementa:
- Endpoints para listar sistemas disponíveis;
- Endpoints para listar, criar e deletar credenciais de autenticação;
- Funções auxiliares para manipulação de licenças de usuários.

Retorna respostas JSON para operações de consulta e manipulação de credenciais.
"""

from asyncio import iscoroutinefunction
from pathlib import Path
from traceback import format_exception
from typing import TYPE_CHECKING, TypedDict

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
from werkzeug.utils import secure_filename

from crawjud.api import db
from crawjud.interfaces.credentials import CredendialsDict
from crawjud.interfaces.session import SessionDict
from crawjud.models import BotsCrawJUD, Credentials, LicensesUsers, Users

cred = Blueprint("creds", __name__)

if TYPE_CHECKING:
    from werkzeug.datastructures import MultiDict


class CredentialsForm(TypedDict):
    """Define o formato do formulário de credenciais para autenticação.

    Args:
        doc_cert (str): Documento do certificado digital.
        nome_cred (str): Nome da credencial.
        system (str): Sistema ao qual a credencial pertence.
        auth_method (str): Método de autenticação utilizado.
        login (str): Login do usuário.
        password (str): Senha do usuário.
        cert (FileStorage): Arquivo do certificado digital.
        key (str): Chave privada do certificado.


    """

    doc_cert: str
    nome_cred: str
    system: str
    auth_method: str
    login: str
    password: str
    cert: FileStorage
    key: str


def license_user(usr: int, db: SQLAlchemy) -> str:
    """Recupera o token de licença associado ao usuário informado.

    Args:
        usr (int): Identificador do usuário.
        db (SQLAlchemy): Instância do banco de dados.

    Returns:
        str: Token de licença do usuário consultado.


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
    """Retorna lista de sistemas disponíveis para autenticação.

    Args:
        Nenhum.

    Returns:
        Response: Resposta JSON contendo os sistemas disponíveis.

    Raises:
        Nenhuma exceção específica.

    """
    list_systems: list[dict[str, str]] = [
        {"value": None, "text": "Escolha um sistema", "disabled": True},
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


@cred.post("/credentials")
@jwt_required
async def credentials() -> Response:
    """Retorna lista de credenciais associadas ao usuário autenticado.

    Returns:
        Response: Resposta JSON contendo as credenciais do usuário.


    """
    try:
        sess = SessionDict(**{
            k: v for k, v in session.items() if not k.startswith("_")
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
                ),
            )

        return await make_response(jsonify(database=credentials), 200)

    except ValueError as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)


@cred.route("/peform_credencial", methods=["POST", "DELETE"])
@jwt_required
async def cadastro() -> Response:
    """Realiza cadastro ou exclusão de credenciais conforme ação informada.

    Args:
        Nenhum argumento direto. Utiliza dados do request para processar
        cadastro ou exclusão de credenciais.

    Returns:
        Response: Resposta JSON indicando sucesso ou falha da operação.


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
                jsonify(message="Credencial deletada com sucesso!"),
                200,
            )

        form = CredentialsForm(**request_data)

        def pw(form: CredentialsForm) -> None:
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
                LicensesUsers.license_token == license_user(get_jwt_identity(), db),
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
                .joinpath(secure_filename(filecert.filename)),
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
                    == license_user(get_jwt_identity(), db),
                ).first()

                passwd.license_usr = licenseusr

                db.session.add(passwd)
                db.session.commit()

        callables = {"cert": cert, "pw": pw}

        call_method = callables[form["auth_method"]]

        if iscoroutinefunction(call_method):
            await call_method(form)
        else:
            call_method(form)

        return await make_response(jsonify(message="Credencial salva com sucesso!"))

    except ValueError as e:
        app.logger.error("\n".join(format_exception(e)))
        abort(500)
