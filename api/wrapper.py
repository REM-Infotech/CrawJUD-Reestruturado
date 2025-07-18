"""Fornece wrappers utilitários para autenticação JWT em endpoints WebSocket.

Inclui decorador para validação de token JWT em conexões WebSocket.
"""

import functools  # noqa: D100
from contextlib import suppress
from typing import Any, Callable

from quart import request
from quart_jwt_extended import decode_token

from api import io
from crawjud.types import WrappedFnReturnT


def verify_jwt_websocket(func: Callable) -> WrappedFnReturnT:  # noqa: ANN001, D103
    """
    Valida o token JWT presente nos cookies da requisição WebSocket.

    Args:
        func (Callable): Função assíncrona a ser decorada.

    Returns:
        WrappedFnReturnT: Função decorada que verifica o JWT antes de executar a função original.

    Observações:
        Emite o evento "not_logged" no namespace "/main" caso o token seja inválido.

    """

    @functools.wraps(func)
    async def decorated_function(*args, **kwargs) -> Any:  # noqa: ANN002, ANN003, ANN202
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
