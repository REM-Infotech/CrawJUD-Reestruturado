"""Fornece decoradores e funções utilitárias para manipulação de CORS.

Este módulo inclui:
- Decoradores para validação de JWT em WebSocket.
- Funções para normalização de métodos, cabeçalhos e origem para CORS.
- Função para adicionar cabeçalhos CORS às respostas HTTP.
"""

from __future__ import annotations

import functools
from contextlib import suppress
from datetime import timedelta
from functools import update_wrapper
from typing import TYPE_CHECKING, AnyStr, ParamSpec

from quart import (
    Response,
    abort,
    current_app,
    make_response,
    request,
)
from quart_jwt_extended import decode_token

from api import io

P = ParamSpec("P", bound=AnyStr)
if TYPE_CHECKING:
    from collections.abc import Callable


def verify_jwt_websocket[T](func: Callable) -> T:
    """Valida o token JWT presente nos cookies da requisição WebSocket.

    Args:
        func (Callable): Função assíncrona a ser decorada.

    Returns:
        Função decorada que verifica o JWT antes
            de executar a função original.

    Observações:
        Emite o evento "not_logged" no namespace "/main" caso o token seja inválido.

    """

    @functools.wraps(func)
    async def decorated_function[T](*args, **kwargs) -> T:  # noqa: ANN002, ANN003
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


def _normalize_methods(methods: list[str] | None) -> str | None:
    """Normaliza os métodos HTTP para cabeçalho CORS.

    Args:
        methods (list[str] | None): Lista de métodos HTTP ou None.

    Returns:
        str | None: Métodos HTTP normalizados em string ou None.

    """
    return ", ".join(sorted(x.upper() for x in methods)) if methods else None


def _normalize_headers(headers: list[str] | None) -> str | None:
    """Normaliza os cabeçalhos para CORS.

    Args:
        headers (list[str] | None): Lista de cabeçalhos HTTP ou None.

    Returns:
        str | None: Cabeçalhos normalizados em string ou None.

    """
    if headers and not isinstance(headers, str):
        return ", ".join(x.upper() for x in headers)
    return headers


def _normalize_origin(origin: str | None) -> str | None:
    """Normaliza a origem para CORS.

    Args:
        origin (str | None): Origem permitida para CORS.

    Returns:
        str | None: Origem normalizada como string ou None.

    """
    if isinstance(origin, str):
        return origin
    if origin:
        return ", ".join(origin)
    return None


def _normalize_max_age(max_age: int | timedelta) -> int:
    """Normaliza o tempo máximo de cache para CORS.

    Args:
        max_age (int | timedelta): Tempo máximo de cache em segundos ou timedelta.

    Returns:
        int: Tempo máximo de cache em segundos.

    """
    return int(max_age.total_seconds()) if isinstance(max_age, timedelta) else max_age


def _get_methods(normalized_methods: str | None) -> str:
    """Obtém os métodos permitidos para CORS.

    Returns:
        str: Métodos HTTP permitidos, formatados para cabeçalho CORS.

    """
    if normalized_methods is not None:
        return normalized_methods
    options_resp = current_app.make_default_options_response()
    return options_resp.headers["allow"]


async def _handle_options() -> Response:
    """Gera resposta para método OPTIONS.

    Returns:
        Response: Resposta padrão para o método OPTIONS.

    """
    return await current_app.make_default_options_response()


async def _handle_post[T](
    f: Callable,
    *args: T,
    **kwargs: T,
) -> Response:
    """Processa requisição POST com verificação de XSRF.

    Returns:
        Response: Resposta HTTP gerada após o processamento do POST.

    """
    name_ = f.__globals__.get("__name__")
    if name_ == "quart_jwt_extended.view_decorators":
        cookie_xsrf_name = current_app.config.get("JWT_ACCESS_CSRF_COOKIE_NAME")
        header_xsrf_name = current_app.config.get("JWT_ACCESS_CSRF_HEADER_NAME")
        xsrf_token = request.cookies.get(cookie_xsrf_name, None)
        if not xsrf_token:
            abort(401, message="Missing XSRF Token")
        request.headers.set(header_xsrf_name, xsrf_token)
    return await make_response(await f(*args, **kwargs))


def _set_cors_headers(
    resp: Response,
    normalized_origin: str | None,
    normalized_methods: str | None,
    normalized_headers: str | None,
    normalized_max_age: int,
) -> None:
    """Define os cabeçalhos CORS na resposta."""
    h = resp.headers
    h["Access-Control-Allow-Origin"] = normalized_origin
    h["Access-Control-Allow-Methods"] = _get_methods(normalized_methods)
    h["Access-Control-Max-Age"] = str(normalized_max_age)
    if normalized_headers is not None:
        h["Access-Control-Allow-Headers"] = normalized_headers


def crossdomain[T](
    origin: str | None = None,
    methods: list[str] | None = None,
    headers: list[str] | None = None,
    max_age: int = 21600,
    *,
    attach_to_all: bool = True,
    automatic_options: bool = True,
) -> Callable[P, Callable[P, T | None]]:
    """Adiciona cabeçalhos CORS à resposta HTTP.

    Args:
        origin (str | None): Origem permitida para CORS.
        methods (list[str] | None): Métodos HTTP permitidos.
        headers (list[str] | None): Cabeçalhos permitidos.
        max_age (int): Tempo máximo de cache dos cabeçalhos CORS.
        attach_to_all (bool): Se deve anexar cabeçalhos a todas respostas.
        automatic_options (bool): Se deve gerar resposta automática para OPTIONS.

    Returns:
        Callable: Decorador que adiciona cabeçalhos CORS à resposta.

    """
    normalized_methods = _normalize_methods(methods)
    normalized_headers = _normalize_headers(headers)
    normalized_origin = _normalize_origin(origin)
    normalized_max_age = _normalize_max_age(max_age)

    def decorator[T](
        f: Callable[P, T],
    ) -> Callable[P, T | None]:
        async def wrapped_function(
            *args: P.args,
            **kwargs: P.kwargs,
        ) -> Response:
            if automatic_options and request.method == "OPTIONS":
                resp = await _handle_options()
            elif request.method == "POST":
                resp = await _handle_post(f, *args, **kwargs)
            else:
                resp = await make_response(await f(*args, **kwargs))

            if not attach_to_all and request.method != "OPTIONS":
                return await resp

            _set_cors_headers(
                resp,
                normalized_origin,
                normalized_methods,
                normalized_headers,
                normalized_max_age,
            )
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator
