"""PATH-029: ASGI normalization fixtures and wrap-once semantics."""

from __future__ import annotations

from urllib.parse import quote

from starlette._utils import get_route_path
from starlette.types import Scope

from hedron_workbench.config import WorkbenchMode
from hedron_workbench.middleware import WorkbenchPathMiddleware, workbenchify


def _scope(**kwargs: object) -> Scope:
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 1234),
        "server": ("127.0.0.1", 8000),
        "root_path": "",
    }
    scope.update(kwargs)
    return scope


class _NullApp:
    def __init__(self) -> None:
        self.seen: list[Scope] = []

    async def __call__(self, scope: Scope, receive: object, send: object) -> None:
        self.seen.append(scope)


def test_mode_off_is_noop() -> None:
    inner = _NullApp()
    mw = WorkbenchPathMiddleware(inner, mode=WorkbenchMode.OFF)
    incoming = _scope(path="/s/abc/p/1/login", root_path="/s/abc/p/1")
    original = dict(incoming)
    out = mw.normalize_scope(incoming)
    assert out is incoming
    assert incoming == original


def test_strip_session_mount_once() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    incoming = _scope(path="/s/abc/p/1/login", root_path="/s/abc/p/1", raw_path=b"/s/abc/p/1/login")
    out = mw.normalize_scope(incoming)
    # Hedron adaptation: leave path prefixed; Starlette get_route_path strips.
    assert out["path"] == "/s/abc/p/1/login"
    assert out["root_path"] == "/s/abc/p/1"
    assert get_route_path(out) == "/login"


def test_partial_prefix_not_stripped() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    incoming = _scope(path="/api/items", root_path="/content/x/api")
    out = mw.normalize_scope(incoming)
    assert out["path"] == "/api/items"


def test_proxy_port_rest_stripped() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    out = mw.normalize_scope(_scope(path="/s/abc/p/1/home", root_path="/proxy/8050/s/abc/p/1"))
    assert out["path"] == "/s/abc/p/1/home"
    assert out["root_path"] == "/s/abc/p/1"
    assert get_route_path(out) == "/home"


def test_unrelated_proxy_path_untouched() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    out = mw.normalize_scope(_scope(path="/proxy/docs", root_path=""))
    assert out["path"] == "/proxy/docs"


def test_encoded_absolute_target() -> None:
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        expected_origins=("https://wb.example",),
    )
    encoded = "/" + quote("https://wb.example/s/abc/p/1/login")
    out = mw.normalize_scope(_scope(path=encoded, root_path=""))
    assert out["path"] == "/s/abc/p/1/login"
    assert out["query_string"] == b""


def test_expected_mount_supplies_missing_root_path() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.AUTO, expected_mount="/s/abc/p/1")
    out = mw.normalize_scope(_scope(path="/s/abc/p/1/login", root_path=""))
    assert out["root_path"] == "/s/abc/p/1"
    assert get_route_path(out) == "/login"


def test_inactive_auto_mode_is_exact_noop() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.AUTO, active=False)
    incoming = _scope(path="/https%3A//wb.example/s/x", root_path="")
    assert mw.normalize_scope(incoming) is incoming


def test_double_normalize_idempotent() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    first = mw.normalize_scope(
        _scope(path="/s/abc/p/1/x", root_path="/s/abc/p/1", raw_path=b"/s/abc/p/1/x")
    )
    second = mw.normalize_scope(first)
    assert second["path"] == first["path"]
    assert second["raw_path"] == first["raw_path"]
    assert second["root_path"] == first["root_path"]
    assert second["query_string"] == first["query_string"]
    assert get_route_path(second) == get_route_path(first) == "/x"


def test_does_not_mutate_caller_scope() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    incoming = _scope(path="/s/abc/p/1/z", root_path="/s/abc/p/1")
    snapshot = dict(incoming)
    mw.normalize_scope(incoming)
    assert incoming == snapshot


def test_lifespan_passthrough() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    incoming = _scope(type="lifespan")
    assert mw.normalize_scope(incoming) is incoming


def test_workbenchify_wrap_once() -> None:
    inner = _NullApp()
    once = workbenchify(inner)
    twice = workbenchify(once)
    assert twice is once
    assert isinstance(once, WorkbenchPathMiddleware)


def test_path_corpus_remains_idempotent() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.AUTO, expected_mount="/s/fuzz/p/8")
    for suffix in ("", "/", "/login", "/api/items", "/hedron-static/app.css"):
        path = "/s/fuzz/p/8" + suffix
        first = mw.normalize_scope(_scope(path=path, root_path=""))
        second = mw.normalize_scope(first)
        assert second == first


def test_websocket_is_candidate() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    out = mw.normalize_scope(_scope(type="websocket", path="/s/abc/p/1/ws", root_path="/s/abc/p/1"))
    assert get_route_path(out) == "/ws"


def test_034_path_parity_table() -> None:
    import json
    from pathlib import Path

    table = json.loads(
        (Path(__file__).with_name("path_parity_034.json")).read_text(encoding="utf-8")
    )
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON)
    for case in table["cases"]:
        out = mw.normalize_scope(_scope(path=case["path"], root_path=case["root_path"]))
        assert out["path"] == case["expected_path"], case["id"]
        assert out["root_path"] == case["expected_root_path"], case["id"]
        if "expected_route_path" in case:
            assert get_route_path(out) == case["expected_route_path"], case["id"]
