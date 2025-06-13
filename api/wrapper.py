import functools  # noqa: D100
from contextlib import suppress

from quart_jwt_extended import verify_jwt_in_request

from api import io


def jwt_socket_required(namespace: str = "/"):  # noqa: ANN001, ANN201, D103
    def decorator(func) -> None:  # noqa: ANN001
        @functools.wraps(func)
        async def decorated_function(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
            validated = False
            with suppress(Exception):
                await verify_jwt_in_request()
                validated = True

            if not validated:
                io.emit("validate-auth", validated, namespace=namespace)
                return
            return await func(*args, **kwargs)

        return decorated_function

    return decorator
