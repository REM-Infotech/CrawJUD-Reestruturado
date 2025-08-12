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

    async def __call__(self, scope: Scope, receive: Callable, send: Callable) -> None:
        """Processa o escopo ASGI, ajustando cabeçalhos e informações do cliente.

        Args:
            scope (Scope): Escopo da requisição ASGI.
            receive (Callable): Função para receber eventos ASGI.
            send (Callable): Função para enviar eventos ASGI.



        """
        # Verifica se o tipo de escopo é http ou websocket
        host: str | None = None
        if scope["type"] == "http" or scope["type"] == "websocket":
            scope = deepcopy(scope)
            headers = scope["headers"]
            client: str | None = None
            scheme: str | None = None

            if self.mode == "modern":
                value = _get_trusted_value(
                    b"forwarded",
                    headers,
                    self.trusted_hops,
                )
                if value is not None:
                    client, host, scheme = self._parse_forwarded(value)
            else:
                client = _get_trusted_value(
                    b"x-forwarded-for",
                    headers,
                    self.trusted_hops,
                )
                scheme = _get_trusted_value(
                    b"x-forwarded-proto",
                    headers,
                    self.trusted_hops,
                )
                host = _get_trusted_value(
                    b"x-forwarded-host",
                    headers,
                    self.trusted_hops,
                )

            # Atualiza informações do escopo conforme valores confiáveis
            if client is not None:
                scope["client"] = (client, 0)

            if scheme is not None:
                scope["scheme"] = scheme

            if host is not None:
                scope["headers"] = self._replace_host_header(headers, host)

        await self.app(scope, receive, send)

    def _parse_forwarded(
        self,
        value: str,
    ) -> tuple[str | None, str | None, str | None]:
        """Extrai os valores de client, host e scheme do cabeçalho Forwarded.

        Args:
            value (str): Valor do cabeçalho Forwarded.

        Returns:
            tuple[str | None, str | None, str | None]: Tupla com client, host e scheme

        """
        client: str | None = None
        host: str | None = None
        scheme: str | None = None
        for part in value.split(";"):
            if part.startswith("for="):
                client = part[4:].strip()
            elif part.startswith("host="):
                host = part[5:].strip()
            elif part.startswith("proto="):
                scheme = part[6:].strip()
        return client, host, scheme

    def _replace_host_header(
        self,
        headers: list[tuple[bytes, bytes]],
        host: str,
    ) -> list[tuple[bytes, bytes]]:
        """Substitui o cabeçalho 'host' pelos valores confiáveis.

        Args:
            headers (list[tuple[bytes, bytes]]): Lista de cabeçalhos.
            host (str): Valor confiável do host.

        Returns:
            list[tuple[bytes, bytes]]: Lista de cabeçalhos atualizada.

        """
        return [
            (name, header_value)
            for name, header_value in headers
            if name.lower() != b"host"
        ] + [(b"host", host.encode())]


def _get_trusted_value(
    name: bytes,
    headers: Iterable[tuple[bytes, bytes]],
    trusted_hops: int,
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
