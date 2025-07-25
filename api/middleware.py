from __future__ import annotations  # noqa: D100

from copy import deepcopy
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from hypercorn.typing import ASGIFramework, Scope


class ProxyFixMiddleware:  # noqa: D101
    def __init__(  # noqa: D107
        self,
        app: ASGIFramework,
        mode: Literal["legacy", "modern"] = "legacy",
        trusted_hops: int = 1,
    ) -> None:
        self.app = app
        self.mode = mode
        self.trusted_hops = trusted_hops

    async def __call__(self, scope: Scope, receive: Callable, send: Callable) -> None:  # noqa: D102
        # Keep the `or` instead of `in {'http' …}` to allow type narrowing
        host: str | None = None
        if scope["type"] == "http" or scope["type"] == "websocket":
            scope = deepcopy(scope)
            headers = scope["headers"]
            client: str | None = None
            scheme: str | None = None

            if (
                self.mode == "modern"
                and (
                    value := _get_trusted_value(
                        b"forwarded", headers, self.trusted_hops
                    )
                )
                is not None
            ):
                for part in value.split(";"):
                    if part.startswith("for="):
                        client = part[4:].strip()
                    elif part.startswith("host="):
                        host = part[5:].strip()
                    elif part.startswith("proto="):
                        scheme = part[6:].strip()

            else:
                client = _get_trusted_value(
                    b"x-forwarded-for", headers, self.trusted_hops
                )
                scheme = _get_trusted_value(
                    b"x-forwarded-proto", headers, self.trusted_hops
                )
                host = _get_trusted_value(
                    b"x-forwarded-host", headers, self.trusted_hops
                )

            if client is not None:
                scope["client"] = (client, 0)

            if scheme is not None:
                scope["scheme"] = scheme

            if host is not None:
                headers = [
                    (name, header_value)
                    for name, header_value in headers
                    if name.lower() != b"host"
                ]
                headers.append((b"host", host.encode()))
                scope["headers"] = headers

        await self.app(scope, receive, send)


def _get_trusted_value(
    name: bytes, headers: Iterable[tuple[bytes, bytes]], trusted_hops: int
) -> str | None:
    if trusted_hops == 0:
        return None

    values = []
    for header_name, header_value in headers:
        if header_name.lower() == name:
            values.extend([
                value.decode("latin1").strip() for value in header_value.split(b",")
            ])

    if len(values) >= trusted_hops:
        return values[-trusted_hops]

    return None
