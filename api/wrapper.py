"""Fornece wrappers utilitários para autenticação JWT em endpoints WebSocket.

Inclui decorador para validação de token JWT em conexões WebSocket.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from contextlib import suppress
from datetime import timedelta
from functools import update_wrapper
from typing import Any, AnyStr, ParamSpec, TypeVar

from quart import (
    Response,
    abort,
    current_app,
    make_response,
    request,
)
from quart_jwt_extended import decode_token

from api import io
from crawjud_app.types import WrappedFnReturnT

BotParamSpec = ParamSpec("BotParamSpec", bound=AnyStr)
BotTypeVar = TypeVar("BotTypeVar", bound=Response)


def verify_jwt_websocket(func: Callable) -> WrappedFnReturnT:
    """Valida o token JWT presente nos cookies da requisição WebSocket.

    Args:
        func (Callable): Função assíncrona a ser decorada.

    Returns:
        WrappedFnReturnT: Função decorada que verifica o JWT antes de executar a função original.

    Observações:
        Emite o evento "not_logged" no namespace "/main" caso o token seja inválido.

    """

    @functools.wraps(func)
    async def decorated_function(*args, **kwargs) -> Any:  # noqa: ANN002, ANN003
        valid = False
        with suppress(Exception):
            decode_token(
                request.cookies["access_token_cookie"],
                request.cookies["X-Xsrf-Token"],
            )
            valid = True

        if not valid:
            await io.emit("not_logged", namespace="/main")
            return await func(*args, **kwargs)

        return await func(*args, **kwargs)

    return decorated_function


def crossdomain(  # noqa: D103
    origin: str | None = None,
    methods: list[str] | None = None,
    headers: list[str] | None = None,
    max_age: int = 21600,
    attach_to_all: bool = True,
    automatic_options: bool = True,
) -> Callable[BotParamSpec, Callable[BotParamSpec, BotTypeVar | None]]:
    if methods is not None:
        methods = ", ".join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ", ".join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ", ".join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods() -> str:
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers["allow"]

    def decorator(
        f: Callable[BotParamSpec, BotTypeVar],
    ) -> Callable[BotParamSpec, BotTypeVar | None]:
        async def wrapped_function(
            *args: BotParamSpec.args,
            **kwargs: BotParamSpec.kwargs,
        ) -> Response:
            _name = f.__globals__.get("__name__")
            if automatic_options and request.method == "OPTIONS":
                resp = await current_app.make_default_options_response()

            elif (
                request.method == "POST"
                and _name == "quart_jwt_extended.view_decorators"
            ):
                cookie_xsrf_name = current_app.config.get(
                    "JWT_ACCESS_CSRF_COOKIE_NAME",
                )
                header_xsrf_name = current_app.config.get(
                    "JWT_ACCESS_CSRF_HEADER_NAME",
                )
                xsrf_token = request.cookies.get(cookie_xsrf_name, None)
                if not xsrf_token:
                    abort(401, message="Missing XSRF Token")

                request.headers.set(header_xsrf_name, xsrf_token)
                resp = await make_response(await f(*args, **kwargs))

            else:
                resp = await make_response(await f(*args, **kwargs))
            if not attach_to_all and request.method != "OPTIONS":
                return await resp

            h = resp.headers

            h["Access-Control-Allow-Origin"] = origin
            h["Access-Control-Allow-Methods"] = get_methods()
            h["Access-Control-Max-Age"] = str(max_age)
            if headers is not None:
                h["Access-Control-Allow-Headers"] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator
