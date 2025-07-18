"""
Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

import quart_flask_patch  # noqa: F401
from quart import (
    Response,
    jsonify,
    make_response,
    request,
)
from quart import current_app as app
from quart_jwt_extended import jwt_required, unset_jwt_cookies
from werkzeug.exceptions import HTTPException

# @app.route("/pjeOffice/requisicao/", methods=["GET", "POST"])
# async def teste():
#     with suppress(Exception):
#         pje_data = app.json.loads(request.args.get("r"))
#         pje_data.update({"u": request.args.get("u", "0")})

#     with suppress(Exception):
#         task = app.json.loads(pje_data.get("tarefa", "{}"))

#     data = await request.data
#     form = await request.form
#     files = await request.files
#     _json = await request.json
#     return jsonify(ok="ok")


@app.route("/", methods=["GET"], websocket=True)
@jwt_required
async def index() -> Response:
    """
    Redirect to the authentication login page.

    Returns:
        Response: A Quart redirect response to the login page.

    """
    return await make_response(jsonify(message="ok"), 200)


@app.errorhandler(HTTPException)
async def handle_http_exception(error: HTTPException) -> Response:
    """
    Handle HTTP exceptions and render a custom error page.

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
    """
    Add CORS headers to the response.

    Args:
        response (Response): The HTTP response object.

    Returns:
        Response: The modified HTTP response object with CORS headers.

    """
    if request.path == "/logout":
        unset_jwt_cookies(response)

    return response  # noqa: ERA001
