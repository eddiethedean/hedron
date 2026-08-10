"""PAGE HTMX core must precede bundled extensions in document order (#55)."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Mount

from hedron import Hedron, Page, Text
from hedron_core import reset_registry_for_tests


@pytest.fixture(autouse=True)
def _fresh_registry() -> None:
    reset_registry_for_tests()
    import hedron_core

    hedron_core._register_builtins()  # type: ignore[attr-defined]
    yield


_SCRIPT_SRC = re.compile(r'<script\b[^>]*\bsrc="([^"]+)"[^>]*>', re.IGNORECASE)


def _script_srcs(html: str) -> list[str]:
    return _SCRIPT_SRC.findall(html)


def _assert_htmx_before_extensions(html: str, *, static_prefix: str = "/hedron-static") -> None:
    srcs = _script_srcs(html)
    core = f"{static_prefix}/htmx.min.js"
    head_support = f"{static_prefix}/ext/head-support.js"
    sse = f"{static_prefix}/ext/sse.js"
    assert core in srcs, html
    assert head_support in srcs, html
    assert sse in srcs, html
    core_i = srcs.index(core)
    assert srcs.index(head_support) > core_i
    assert srcs.index(sse) > core_i
    assert html.count(core) == 1
    assert html.count(head_support) == 1
    assert html.count(sse) == 1


def test_page_injects_htmx_core_before_bundled_extensions() -> None:
    app = Hedron(title="order", security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Page:
        return Page(Text("ok"), title="Order")

    response = TestClient(app).get("/")
    assert response.status_code == 200
    _assert_htmx_before_extensions(response.text)


def test_mounted_page_injects_htmx_core_before_bundled_extensions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ROOT_PATH", "/app")
    inner = Hedron(
        title="order-mounted",
        security="standard",
        explorer="off",
        session_secret="test-secret-mounted",
    )

    @inner.page("/")
    def home() -> Page:
        return Page(Text("mounted"), title="Mounted")

    client = TestClient(Starlette(routes=[Mount("/app", app=inner)]))
    response = client.get("/app/")
    assert response.status_code == 200
    _assert_htmx_before_extensions(response.text, static_prefix="/app/hedron-static")


def test_duplicate_htmx_and_extension_assets_are_not_reinjected() -> None:
    from starlette.requests import Request

    from hedron.responses import _inject_htmx_extension_assets
    from hedron.security.policy import SecurityPolicy

    class _State:
        hedron_mount_path = ""
        hedron_security = SecurityPolicy.from_name("standard")

    class _App:
        state = _State()

    request = Request({"type": "http", "method": "GET", "path": "/", "headers": [], "app": _App()})
    seeded = (
        "<!DOCTYPE html><html><head>"
        '<script src="/hedron-static/htmx.min.js" defer></script>'
        '<script src="/hedron-static/ext/head-support.js" defer></script>'
        '<script src="/hedron-static/ext/sse.js" defer></script>'
        "</head><body>ok</body></html>"
    )
    once = _inject_htmx_extension_assets(seeded, request)
    twice = _inject_htmx_extension_assets(once, request)
    assert twice.count("/hedron-static/htmx.min.js") == 1
    assert twice.count("/hedron-static/ext/head-support.js") == 1
    assert twice.count("/hedron-static/ext/sse.js") == 1
    _assert_htmx_before_extensions(twice)
