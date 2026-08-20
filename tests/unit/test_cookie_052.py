"""COOKIE-052 evidence."""

from __future__ import annotations

from starlette.responses import Response

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
