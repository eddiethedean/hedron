"""CONTEXT-052 evidence."""

from __future__ import annotations

from starlette.requests import Request

from hedron_posit import HedronPosit, PositConfig, PositContext
from hedron_posit.config import WorkbenchConfig, WorkbenchMode


def test_posit_for_returns_request_bound_context() -> None:
    app = HedronPosit(
        title="context-052",
        posit=PositConfig(
            workbench=WorkbenchConfig(mode=WorkbenchMode.ON, mount="/s/abc/p/xyz/"),
        ),
    )

    @app.get("/profile")
    async def profile() -> dict[str, str]:
        return {"ok": "1"}

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "https",
        "path": "/profile",
        "raw_path": b"/profile",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("test", 443),
        "root_path": "/s/abc/p/xyz",
        "app": app,
    }
    request = Request(scope)
    ctx = app.posit_for(request)
    assert isinstance(ctx, PositContext)
    assert ctx.href("/profile", query={"tab": "1"}).endswith("/profile?tab=1")
    assert "/s/abc/p/xyz" in ctx.href("/profile")
    caps = ctx.capabilities()
    assert caps.platform in {"workbench", "hedron", "connect"}
