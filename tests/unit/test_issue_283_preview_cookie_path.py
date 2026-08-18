"""#283: PreviewTokenGate must not seed cookies from unsanitized root_path."""

from __future__ import annotations

import pytest

from hedron_notebook import PREVIEW_TOKEN_QUERY, wrap_preview_app


async def _ok_app(scope: dict[str, object], receive: object, send: object) -> None:
    del receive
    assert callable(send)
    await send(  # type: ignore[misc]
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send({"type": "http.response.body", "body": b"ok"})  # type: ignore[misc]


@pytest.mark.anyio
async def test_preview_gate_skips_cookie_on_unsafe_root_path() -> None:
    gated = wrap_preview_app(_ok_app, "secret-token")
    messages: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        messages.append(message)

    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    scope: dict[str, object] = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/",
        "raw_path": b"/",
        "query_string": f"{PREVIEW_TOKEN_QUERY}=secret-token".encode(),
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("preview.test", 80),
        "root_path": "/ok; Secure; Domain=evil.com",
    }
    await gated(scope, receive, send)
    start = next(item for item in messages if item.get("type") == "http.response.start")
    headers = list(start.get("headers") or ())
    assert all(name.lower() != b"set-cookie" for name, _ in headers)
    raw_values = b" ".join(value for _, value in headers)
    assert b"Domain=evil.com" not in raw_values
    assert start.get("status") == 200
