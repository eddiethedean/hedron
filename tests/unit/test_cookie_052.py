"""COOKIE-052 evidence."""

from __future__ import annotations

from starlette.responses import Response
from starlette.testclient import TestClient

from hedron_posit import CookieSpec, HedronPosit, PositConfig, resolve_cookie_path
from hedron_posit.config import WorkbenchConfig, WorkbenchMode


def test_resolve_cookie_path_never_auto() -> None:
    assert resolve_cookie_path("auto") == "/"
    assert resolve_cookie_path("/s/abc/p/xyz/") == "/s/abc/p/xyz"
    assert "auto" not in resolve_cookie_path("/content/app/").lower()


def test_cookie_registry_set_delete_matching_path() -> None:
    app = HedronPosit(
        title="cookie-052",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
        session_secret="test-secret-cookie-052",
    )
    app.register_cookie(CookieSpec(name="app_session"))
    response = Response("ok")
    app.cookies.set(response, "app_session", "secret-value")
    headers = [
        value.decode("latin-1")
        for key, value in response.raw_headers
        if key.lower() == b"set-cookie"
    ]
    assert headers
    assert "Path=/s/abc/p/xyz" in headers[0]
    assert "Path=auto" not in headers[0]
    assert "secret-value" in headers[0]
    app.cookies.delete(response, "app_session")
    delete_headers = [
        value.decode("latin-1")
        for key, value in response.raw_headers
        if key.lower() == b"set-cookie"
    ]
    assert any("Path=/s/abc/p/xyz" in item for item in delete_headers)


def test_late_register_cookie_is_owned_by_middleware() -> None:
    app = HedronPosit(
        title="cookie-late",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
        session_secret="test-secret-cookie-late",
    )
    app.register_cookie(CookieSpec(name="late_cookie"))
    assert "late_cookie" in app._workbench_asgi.owned_cookie_names

    @app.get("/set")
    async def set_cookie() -> Response:
        response = Response("ok")
        response.set_cookie("late_cookie", "v", path="/")
        return response

    client = TestClient(app)
    response = client.get("/set")
    header = response.headers.get("set-cookie", "")
    assert "late_cookie=" in header
    assert "Path=/s/abc/p/xyz" in header or "Path=/s/abc/p/xyz;".lower() in header.lower()
    assert "Path=auto" not in header


def test_cookies_register_refreshes_middleware_owned_names() -> None:
    app = HedronPosit(
        title="cookie-register-api",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
        session_secret="test-secret-cookie-register-api",
    )
    app.cookies.register(CookieSpec(name="bypass_cookie"))
    assert "bypass_cookie" in app._workbench_asgi.owned_cookie_names
    assert app.posit_status().registered_cookie_count >= 4

    @app.get("/set")
    async def set_cookie() -> Response:
        response = Response("ok")
        response.set_cookie("bypass_cookie", "v", path="/")
        return response

    client = TestClient(app)
    response = client.get("/set")
    header = response.headers.get("set-cookie", "")
    assert "Path=/s/abc/p/xyz" in header
    assert "Path=auto" not in header


def test_middleware_rewrites_literal_path_auto_for_owned_cookies() -> None:
    app = HedronPosit(
        title="cookie-auto",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
        session_secret="test-secret-cookie-auto",
    )

    @app.get("/set")
    async def set_cookie() -> Response:
        response = Response("ok")
        response.set_cookie("session", "secret", path="auto")
        return response

    client = TestClient(app)
    response = client.get("/set")
    header = response.headers.get("set-cookie", "")
    assert "Path=auto" not in header
    assert "Path=/s/abc/p/xyz" in header
