"""
Module for main application routes.

This module defines global routes, context processors, and custom error handling.
"""

import quart_flask_patch  # noqa: F401
from quart import (
    Response,
    jsonify,
    make_response,
)
from quart import current_app as app
from quart_jwt_extended import jwt_required
from werkzeug.exceptions import HTTPException


@app.route("/", methods=["GET"])
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


# @app.after_request
# async def after_request(response: Response) -> Response:
#     """
#     Add CORS headers to the response.

#     Args:
#         response (Response): The HTTP response object.

#     Returns:
#         Response: The modified HTTP response object with CORS headers.

#     """
#     response.headers["Access-Control-Allow-Origin"] = "*"  # noqa: ERA001
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"  # noqa: ERA001
#     return response  # noqa: ERA001
