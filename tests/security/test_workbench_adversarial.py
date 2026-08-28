"""Security adversarial corpus for the Posit Workbench adapter."""

from __future__ import annotations

import asyncio
from urllib.parse import quote

import pytest

from hedron.mount import normalize_mount_path, prefix_local_path
from hedron_core.diagnostics import HedronError
from hedron_posit.config import WorkbenchConfig
from hedron_posit.middleware import WorkbenchPathMiddleware
from hedron_posit.redact import redact_scope_for_log, redact_text
from hedron_posit.resolve import parse_rserver_url_output, resolve_deployment
from hedron_posit.runner import discover_rserver_url


class _Null:
    async def __call__(self, scope: object, receive: object, send: object) -> None:
        return None


def test_traversal_mount_rejected() -> None:
    assert normalize_mount_path("/s/x/../evil") == ""
    assert prefix_local_path("/login", "/s/x/../evil") == "/login"


def test_protocol_relative_rserver_rejected() -> None:
    with pytest.raises(HedronError):
        parse_rserver_url_output("//evil.example/s/x", port=1)


def test_credentials_in_rserver_url_rejected() -> None:
    with pytest.raises(HedronError):
        parse_rserver_url_output("https://user:token@wb.example/s/x", port=1)


def test_shell_not_used_for_relative_binary() -> None:
    with pytest.raises(HedronError) as exc:
        discover_rserver_url(binary="rserver-url; rm -rf /", port=1)
    assert "HED-WB-0003" in str(exc.value)


def test_untrusted_header_not_a_mount() -> None:
    resolved = resolve_deployment(WorkbenchConfig(), environ={})
    assert resolved.browser_mount == ""


def test_encoded_dot_target_not_stripped() -> None:
    mw = WorkbenchPathMiddleware(_Null(), mode="on")
    scope = {
        "type": "http",
        "path": "/s/%2e%2e/login",
        "root_path": "/s/abc",
        "raw_path": b"/s/%2e%2e/login",
        "query_string": b"",
        "method": "GET",
    }
    out = mw.normalize_scope(scope)  # type: ignore[arg-type]
    assert out["path"] != "/login"


def test_redaction_covers_license_and_query() -> None:
    assert "26TA" not in redact_text("PWB_LICENSE=6IX8-R4P6-UDJS-BIE5-UGAH-8XSS-26TA")
    redacted = redact_scope_for_log(
        {
            "method": "GET",
            "root_path": "/s/4566a3c9ab5a7ad01e1a7/p/1",
            "path": "/s/4566a3c9ab5a7ad01e1a7/p/1",
            "raw_path": b"/s/4566a3c9ab5a7ad01e1a7/p/1",
            "query_string": b"token=supersecret&q=ok",
        }
    )
    assert "4566a3c9ab5a7ad01e1a7" not in str(redacted["path"])
    assert "supersecret" not in str(redacted["query_string"])
    assert "***" in str(redacted["query_string"])


def _run_asgi(middleware: WorkbenchPathMiddleware, scope: dict[str, object]) -> list[dict]:
    messages: list[dict] = []

    async def receive() -> dict:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict) -> None:
        messages.append(message)

    asyncio.run(middleware(scope, receive, send))  # type: ignore[arg-type]
    return messages


def test_adversarial_absolute_target_returns_400() -> None:
    mw = WorkbenchPathMiddleware(_Null(), mode="on", expected_origins=("https://wb.example",))
    target = "/" + quote("https://wb.example/s/x/../admin", safe="")
    messages = _run_asgi(
        mw,
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": target,
            "raw_path": target.encode(),
            "root_path": "",
            "query_string": b"",
            "headers": [],
        },
    )
    assert messages[0]["status"] == 400


def test_oversized_target_returns_414() -> None:
    mw = WorkbenchPathMiddleware(_Null(), mode="on")
    target = "/" + "x" * 9000
    messages = _run_asgi(
        mw,
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": target,
            "raw_path": target.encode(),
            "root_path": "",
            "query_string": b"",
            "headers": [],
        },
    )
    assert messages[0]["status"] == 414


def test_conflicting_absolute_target_query_returns_400() -> None:
    mw = WorkbenchPathMiddleware(_Null(), mode="on", expected_origins=("https://wb.example",))
    target = "/" + quote("https://wb.example/s/x?token=one", safe="")
    messages = _run_asgi(
        mw,
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": target,
            "raw_path": target.encode(),
            "root_path": "",
            "query_string": b"token=two",
            "headers": [],
        },
    )
    assert messages[0]["status"] == 400


@pytest.mark.parametrize(
    "absolute",
    [
        "https://evil.example/s/x/admin",
        "https://user:pass@wb.example/s/x/admin",
        "https://wb.example:99999/s/x/admin",
        "https://wb.example/s/x/admin#fragment",
    ],
)
def test_absolute_target_origin_is_bound_to_discovered_origin(absolute: str) -> None:
    mw = WorkbenchPathMiddleware(_Null(), mode="on", expected_origins=("https://wb.example",))
    target = "/" + quote(absolute, safe="")
    messages = _run_asgi(
        mw,
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": target,
            "raw_path": target.encode(),
            "root_path": "",
            "query_string": b"",
            "headers": [],
        },
    )
    assert messages[0]["status"] == 400
