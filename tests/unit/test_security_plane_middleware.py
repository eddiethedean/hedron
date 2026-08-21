"""HTTP lifecycle for SecurityPlaneMiddleware bind / clear / isolation."""

from __future__ import annotations

from fastapi import Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from hedron import Hedron
from hedron_core.security_context import get_security_context


def test_security_plane_middleware_binds_and_clears_per_request() -> None:
    app = Hedron(
        title="plane",
        security="standard",
        session_secret="secret-for-tests-32chars-ok!!",
        explorer="off",
    )
    seen: list[object] = []
    bindings: list[object] = []

    @app.get("/probe")
    def probe(request: Request) -> dict[str, bool]:
        ctx = get_security_context()
        seen.append(ctx)
        bindings.append(getattr(request.state, "hedron_security_binding", None))
        assert ctx is not None
        assert ctx.application_id
        return {"ok": True}

    client = TestClient(app)
    assert client.get("/probe").status_code == 200
    assert client.get("/probe").status_code == 200
    assert seen[0] is not None and seen[1] is not None
    assert seen[0] is not seen[1]
    assert bindings[0] is not None and bindings[1] is not None
    assert bindings[0] is not bindings[1]
    assert get_security_context() is None


def test_security_plane_middleware_clears_on_handler_error() -> None:
    app = Hedron(
        title="plane-err",
        security="standard",
        session_secret="secret-for-tests-32chars-ok!!",
        explorer="off",
    )
    observed: list[object] = []

    @app.get("/boom", response_model=None)
    def boom() -> dict[str, str]:
        observed.append(get_security_context())
        raise RuntimeError("plane boom")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/boom")
    assert response.status_code == 500
    assert observed[0] is not None
    assert get_security_context() is None


def test_security_plane_middleware_propagates_correlation_id() -> None:
    app = Hedron(
        title="plane-corr",
        security="standard",
        session_secret="secret-for-tests-32chars-ok!!",
        explorer="off",
    )
    seen: list[str] = []

    @app.get("/corr")
    def corr() -> JSONResponse:
        ctx = get_security_context()
        assert ctx is not None
        seen.append(ctx.correlation_id)
        return JSONResponse({"ok": True})

    client = TestClient(app)
    assert client.get("/corr", headers={"X-Request-Id": "req-42"}).status_code == 200
    assert seen == ["req-42"]
