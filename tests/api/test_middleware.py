import pytest
from api.middleware import ProxyFixMiddleware, _get_trusted_value

class DummyApp:
    """Simula um aplicativo ASGI para testes."""
    def __init__(self):
        self.last_scope = None

    async def __call__(self, scope, receive, send):
        self.last_scope = scope

@pytest.mark.asyncio
async def test_proxyfixmiddleware_legacy_mode_updates_scope():
    app = DummyApp()
    middleware = ProxyFixMiddleware(app, mode="legacy", trusted_hops=1)
    scope = {
        "type": "http",
        "headers": [
            (b"x-forwarded-for", b"1.2.3.4"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"example.com"),
            (b"host", b"original.com"),
        ],
        "client": ("0.0.0.0", 0),
        "scheme": "http",
    }
    async def dummy_receive(): pass
    async def dummy_send(x): pass

    await middleware(scope, dummy_receive, dummy_send)
    updated_scope = app.last_scope
    assert updated_scope["client"][0] == "1.2.3.4"
    assert updated_scope["scheme"] == "https"
    assert (b"host", b"example.com") in updated_scope["headers"]
    assert all(h[1] != b"original.com" for h in updated_scope["headers"])

@pytest.mark.asyncio
async def test_proxyfixmiddleware_modern_mode_updates_scope():
    app = DummyApp()
    middleware = ProxyFixMiddleware(app, mode="modern", trusted_hops=1)
    scope = {
        "type": "http",
        "headers": [
            (b"forwarded", b"for=5.6.7.8;host=modern.com;proto=https"),
            (b"host", b"legacy.com"),
        ],
        "client": ("0.0.0.0", 0),
        "scheme": "http",
    }
    async def dummy_receive(): pass
    async def dummy_send(x): pass

    await middleware(scope, dummy_receive, dummy_send)
    updated_scope = app.last_scope
    assert updated_scope["client"][0] == "5.6.7.8"
    assert updated_scope["scheme"] == "https"
    assert (b"host", b"modern.com") in updated_scope["headers"]
    assert all(h[1] != b"legacy.com" for h in updated_scope["headers"])

@pytest.mark.asyncio
async def test_proxyfixmiddleware_trusted_hops_zero_does_not_update():
    app = DummyApp()
    middleware = ProxyFixMiddleware(app, mode="legacy", trusted_hops=0)
    scope = {
        "type": "http",
        "headers": [
            (b"x-forwarded-for", b"1.2.3.4"),
            (b"x-forwarded-proto", b"https"),
            (b"x-forwarded-host", b"example.com"),
            (b"host", b"original.com"),
        ],
        "client": ("0.0.0.0", 0),
        "scheme": "http",
    }
    async def dummy_receive(): pass
    async def dummy_send(x): pass

    await middleware(scope, dummy_receive, dummy_send)
    updated_scope = app.last_scope
    assert updated_scope["client"][0] == "0.0.0.0"
    assert updated_scope["scheme"] == "http"
    assert (b"host", b"original.com") in updated_scope["headers"]

def test_parse_forwarded_variations():
    middleware = ProxyFixMiddleware(DummyApp())
    # Caso completo
    client, host, scheme = middleware._parse_forwarded("for=1.1.1.1;host=test.com;proto=https")
    assert client == "1.1.1.1"
    assert host == "test.com"
    assert scheme == "https"
    # Caso parcial
    client, host, scheme = middleware._parse_forwarded("for=2.2.2.2;proto=http")
    assert client == "2.2.2.2"
    assert host is None
    assert scheme == "http"
    # Caso sem valores
    client, host, scheme = middleware._parse_forwarded("")
    assert client is None
    assert host is None
    assert scheme is None

def test_replace_host_header_removes_old_and_adds_new():
    middleware = ProxyFixMiddleware(DummyApp())
    headers = [
        (b"host", b"old.com"),
        (b"x-forwarded-for", b"1.2.3.4"),
    ]
    new_headers = middleware._replace_host_header(headers, "new.com")
    assert (b"host", b"new.com") in new_headers
    assert all(h[1] != b"old.com" for h in new_headers)
    assert (b"x-forwarded-for", b"1.2.3.4") in new_headers

def test_get_trusted_value_multiple_hops():
    headers = [
        (b"x-forwarded-for", b"1.1.1.1,2.2.2.2,3.3.3.3"),
    ]
    # trusted_hops=1 deve retornar o último
    assert _get_trusted_value(b"x-forwarded-for", headers, 1) == "3.3.3.3"
    # trusted_hops=2 deve retornar o penúltimo
    assert _get_trusted_value(b"x-forwarded-for", headers, 2) == "2.2.2.2"
    # trusted_hops=3 deve retornar o primeiro
    assert _get_trusted_value(b"x-forwarded-for", headers, 3) == "1.1.1.1"
    # trusted_hops maior que quantidade disponível retorna None
    assert _get_trusted_value(b"x-forwarded-for", headers, 4) is None

def test_get_trusted_value_no_header_returns_none():
    headers = [
        (b"host", b"example.com"),
    ]
    assert _get_trusted_value(b"x-forwarded-for", headers, 1) is None
