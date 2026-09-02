"""PATH-029: ASGI normalization fixtures and wrap-once semantics."""

from __future__ import annotations

from urllib.parse import quote, urljoin

import pytest
from starlette._utils import get_route_path
from starlette.types import Scope

from fastapi_workbench.mount import is_local_path
from hedron_posit.config import WorkbenchMode
from hedron_posit.middleware import WorkbenchPathMiddleware, workbenchify


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


def test_malformed_bracketed_targets_fail_closed() -> None:
    assert is_local_path("//]YJnx") is False
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        expected_origins=("https://wb.example",),
    )
    with pytest.raises(Exception) as exc:
        mw.normalize_scope(_scope(path="/http%3a%2f%2f%5d", root_path=""))
    assert getattr(exc.value, "status_code", None) == 400


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


def test_absolute_redirect_rewrite_is_bounded_to_location() -> None:
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        absolute_redirects=True,
        absolute_origin="https://workbench.example",
    )
    message = {
        "type": "http.response.start",
        "status": 303,
        "headers": [
            (b"location", b"/login"),
            (b"hx-redirect", b"/next"),
            (b"hx-push-url", b"/history"),
            (b"hx-replace-url", b"/replace"),
        ],
    }
    rewritten = mw._rewrite_response_start(message, "/s/session/p/1")
    headers = dict(rewritten["headers"])
    assert headers[b"location"] == b"https://workbench.example/s/session/p/1/login"
    assert headers[b"hx-redirect"] == b"/s/session/p/1/next"
    assert headers[b"hx-push-url"] == b"/s/session/p/1/history"
    assert headers[b"hx-replace-url"] == b"/s/session/p/1/replace"


def test_absolute_redirect_rewrite_requires_trusted_origin() -> None:
    with pytest.raises(ValueError, match="absolute_origin"):
        WorkbenchPathMiddleware(
            _NullApp(),
            mode=WorkbenchMode.ON,
            absolute_redirects=True,
        )


def test_path_only_discovery_uses_relative_location_for_both_entry_points() -> None:
    mount = "/s/session-token/p/proxy-token"
    mw = WorkbenchPathMiddleware(
        _NullApp(),
        mode=WorkbenchMode.ON,
        relative_redirects=True,
    )
    message = {
        "type": "http.response.start",
        "status": 303,
        "headers": [(b"location", b"/login")],
    }

    mounted = mw._rewrite_response_start(
        message,
        mount,
        request_path=f"{mount}/go",
    )
    legacy = mw._rewrite_response_start(
        message,
        mount,
        request_path="/go",
    )

    assert dict(mounted["headers"])[b"location"] == b"login"
    assert dict(legacy["headers"])[b"location"] == b"login"
    assert urljoin(f"https://wb.example{mount}/go", "login") == (f"https://wb.example{mount}/login")
    assert urljoin("https://wb.example/proxy/8000/go", "login") == (
        "https://wb.example/proxy/8000/login"
    )


def test_relative_location_preserves_query_and_fragment() -> None:
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON, relative_redirects=True)
    message = {
        "type": "http.response.start",
        "status": 303,
        "headers": [(b"location", b"/login?next=%2Fhome#done")],
    }
    rewritten = mw._rewrite_response_start(
        message,
        "/s/session/p/1",
        request_path="/s/session/p/1/account/go",
    )
    assert dict(rewritten["headers"])[b"location"] == b"../login?next=%2Fhome#done"


@pytest.mark.parametrize(
    ("target", "request_path", "expected"),
    (
        ("/pipeline", "/pipeline/save", "../pipeline?notice=saved"),
        ("/security", "/security/secrets/mss", "../../security?notice=secret-saved"),
    ),
)
def test_relative_location_spells_out_non_slash_canonical_targets(
    target: str, request_path: str, expected: str
) -> None:
    mount = "/s/session-token/p/proxy-token"
    mw = WorkbenchPathMiddleware(_NullApp(), mode=WorkbenchMode.ON, relative_redirects=True)
    value = f"{mount}{target}?notice={'saved' if target == '/pipeline' else 'secret-saved'}"

    relative = mw._relative_local_redirect(value, mount, f"{mount}{request_path}")

    assert relative == expected
    resolved = urljoin(f"https://wb.example{mount}{request_path}", relative)
    assert resolved.removeprefix("https://wb.example") == (
        f"{mount}{target}?notice={'saved' if target == '/pipeline' else 'secret-saved'}"
    )


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
