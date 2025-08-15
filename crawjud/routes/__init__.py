"""Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

import json

from quart import (
    Response,
    current_app,
    jsonify,
    make_response,
    request,
)
from quart import current_app as app
from quart_jwt_extended import jwt_required, unset_jwt_cookies
from werkzeug.exceptions import HTTPException


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
            current_app.logger.exception(
                f"Erro 401: {error_json.get('description', error_json)}",
            )
        except (KeyError, Exception) as exc:
            current_app.logger.exception(f"Erro 401 sem mensagem detalhada: {exc}")

    return response  # Retorna resposta modificada
