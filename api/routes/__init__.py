"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

# from contextlib import suppress

import json

import quart_flask_patch

# import requests
from quart import (
    Response,
    jsonify,
    make_response,
    request,
)
from quart import current_app as app
from quart_jwt_extended import jwt_required, unset_jwt_cookies
from werkzeug.exceptions import HTTPException

# from addons.assinador import SignPy


# @app.route("/pjeOffice/requisicao/", methods=["GET", "POST"])
# async def teste() -> Response:
#     with suppress(Exception):
#         pje_data = app.json.loads(request.args.get("r"))
#         pje_data.update({"u": request.args.get("u", "0")})

#     with suppress(Exception):
#         _task = app.json.loads(pje_data.get("tarefa", "{}"))

#     _data = await request.data
#     _form = await request.form
#     _files = await request.files
#     _json = await request.json

#     data = SignPy.assinador(
#         "\\\\fmv.intranet\\NETLOGON\\CERTIFICADO\\44555059204.pfx",
#         "123456@Pu",
#         bytearray(_task["mensagem"].encode()),
#     )

#     data_json = {
#         "uuid": _task["token"],
#         "mensagem": _task["mensagem"],
#         "assinatura": data.getSignature64(),
#         "certChain": data.getCertificateChain64(),
#     }
#     url = f"{pje_data['servidor']}{_task['enviarPara']}"

#     # Envia requisição POST com dados JSON e header apropriado

#     cookie = {}

#     for item in pje_data["sessao"].split("; "):
#         key, value = tuple(item.split("="))
#         cookie.update({key: value})

#     _req = requests.post(
#         url,
#         cookies=cookie,
#         json=data_json,
#         headers={"Content-Type": "application/json; charset=UTF-8"},
#         timeout=60,
#     )

#     print(data_json)
#     # Retorna resposta compatível com Quart
#     return await make_response(
#         _req.text,
#         _req.status_code,
#         {"Content-Type": _req.headers.get("Content-Type", "application/json")},
#     )


# @app.route(
#     "/",
#     defaults={"path": ""},
#     methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
# )
# @app.route(
#     "/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
# )
# async def proxy(path) -> Response:
#     print(f"Interceptado: {request.method} /{path}")
#     print(f"Headers: {dict(request.headers)}")
#     print(f"Body: {await request.data}")

#     proxied_url = f"http://127.0.0.1:8800/{path}"
#     response = requests.request(
#         method=request.method,
#         url=proxied_url,
#         headers={k: v for k, v in request.headers if k.lower() != "host"},
#         data=await request.data,
#         allow_redirects=False,
#         timeout=1,
#     )

#     return Response(
#         response.content, status=response.status_code, headers=dict(response.headers)
#     )


@app.route("/", methods=["GET"], websocket=True)
@jwt_required
async def index() -> Response:
    """Redirect to the authentication login page.

    Returns:
        Response: A Quart redirect response to the login page.

    """
    return await make_response(jsonify(message="ok"), 200)


@app.errorhandler(401)
async def handle_http_exception(error: HTTPException) -> Response:
    """Handle HTTP exceptions and render a custom error page.

    Args:
        error (HTTPException): The raised HTTP exception.

    Returns:
        tuple: A tuple containing the rendered error page and the HTTP status code.

    """
    name = error.name
    desc = error.description

    return await make_response(jsonify(name=name, description=desc), error.code)


# @app.before_request
# def load_user():
#     request
#     if "user_id" in session:
#         g.user = db.session.get(session["user_id"])


@app.after_request
async def after_request(response: Response) -> Response:
    """Adicione cabeçalhos CORS e exiba mensagem de erro 401.

    Args:
        response (Response): Objeto de resposta HTTP.

    Returns:
        Response: Objeto de resposta HTTP modificado com cabeçalhos CORS.

    """
    # Verifica se o caminho é /logout para remover cookies JWT
    if request.path == "/logout":
        unset_jwt_cookies(response)

    # Verifica se o status é 401 e exibe mensagem de erro
    if response.status_code == 401:
        # Tenta obter mensagem de erro do corpo da resposta
        try:
            # Decodifica o corpo da resposta para JSON
            error_data = await response.get_data()
            # Converte bytes para string e carrega como JSON
            error_json = json.loads(error_data.decode())
            print(f"Erro 401: {error_json.get('description', error_json)}")
        except Exception as exc:
            print(f"Erro 401 sem mensagem detalhada: {exc}")

    return response  # Retorna resposta modificada
