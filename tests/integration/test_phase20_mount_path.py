"""Phase 0.20 MOUNT-020 trusted mount path helpers."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Mount

from hedron import Hedron, Page, Text, redirect_local
from hedron.mount import (
    cookie_path_for_mount,
    normalize_mount_path,
    prefix_local_path,
    resolve_mount_path,
)
from hedron_core import reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


def test_normalize_and_cookie_path() -> None:
    assert normalize_mount_path("/") == ""
    assert normalize_mount_path("/app/") == "/app"
    assert cookie_path_for_mount("") == "/"
    assert cookie_path_for_mount("/app") == "/app/"


def test_prefix_local_path_once() -> None:
    assert prefix_local_path("/login", "/app") == "/app/login"
    assert prefix_local_path("/app/login", "/app") == "/app/login"
    assert prefix_local_path("/", "/app") == "/app/"


def test_untrusted_forwarded_prefix_ignored() -> None:
    mount = resolve_mount_path(
        root_path=None,
        headers={"x-forwarded-prefix": "/evil"},
        peer="10.0.0.9",
        trusted_peers=["127.0.0.1"],
        prefer_env=False,
    )
    assert mount.path == ""
    assert mount.source == "default"


def test_trusted_peer_prefix_header() -> None:
    mount = resolve_mount_path(
        root_path=None,
        headers={"x-forwarded-prefix": "/app"},
        peer="127.0.0.1",
        trusted_peers=["127.0.0.1"],
        prefer_env=False,
    )
    assert mount.path == "/app"
    assert mount.source.startswith("header:")


def test_env_root_path_scopes_csrf_cookie(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ROOT_PATH", "/app")
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    app = Hedron(title="demo", security="standard", explorer="off", session_secret="test-secret-ok")

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    # Starlette TestClient exposes set-cookie; path should be mount-scoped.
    set_cookie = response.headers.get("set-cookie", "")
    assert "hedron_csrf=" in set_cookie
    assert "Path=/app/" in set_cookie or "path=/app/" in set_cookie.lower()


def test_mount_scoped_csrf_post_succeeds_under_subpath(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CSRF double-submit works when the app is mounted at /app with Path=/app/."""
    monkeypatch.setenv("HEDRON_ROOT_PATH", "/app")
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    inner = Hedron(
        title="mounted",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @inner.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @inner.action("/save")
    def save() -> Page:
        return Page(Text("saved"), title="Saved")

    outer = Starlette(routes=[Mount("/app", app=inner)])
    client = TestClient(outer)
    seeded = client.get("/app/")
    assert seeded.status_code == 200
    set_cookie = seeded.headers.get("set-cookie", "")
    assert "Path=/app/" in set_cookie or "path=/app/" in set_cookie.lower()
    token = seeded.cookies.get("hedron_csrf")
    assert token

    denied = client.post("/app/save")
    assert denied.status_code == 403

    ok = client.post("/app/save", headers={"X-CSRF-Token": token})
    assert ok.status_code == 200
    assert "saved" in ok.text


def test_mount_scoped_csrf_cookie_not_sent_outside_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Path=/app/ cookie must not satisfy CSRF on routes outside the mount path."""
    monkeypatch.setenv("HEDRON_ROOT_PATH", "/app")
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    app = Hedron(
        title="unmounted",
        security="standard",
        explorer="off",
        session_secret="test-secret-ok",
    )

    @app.page("/")
    def home() -> Page:
        return Page(Text("home"), title="Home")

    @app.action("/save")
    def save() -> Page:
        return Page(Text("saved"), title="Saved")

    client = TestClient(app)
    seeded = client.get("/")
    assert seeded.status_code == 200
    set_cookie = seeded.headers.get("set-cookie", "")
    assert "Path=/app/" in set_cookie or "path=/app/" in set_cookie.lower()
    # Extract token from Set-Cookie even if the jar omits Path=/app/ for `/save`.
    token = None
    for part in set_cookie.split(","):
        if "hedron_csrf=" in part:
            token = part.split("hedron_csrf=", 1)[1].split(";", 1)[0].strip()
            break
    assert token
    # Request path `/save` is outside cookie Path=/app/ — double-submit must fail.
    denied = client.post("/save", headers={"X-CSRF-Token": token})
    assert denied.status_code == 403


def test_redirect_local_with_mount() -> None:
    response = redirect_local("/login", mount="/app")
    assert response.headers["location"] == "/app/login"
