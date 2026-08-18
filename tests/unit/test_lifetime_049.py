"""LIFETIME-049 handler/response compilation and background capture."""

from __future__ import annotations

import inspect

from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.unit._helpers_049 import make_app, reset_049

from hedron import DependencyLifetime, DependsOn, Text
from hedron.experimental import SseResponse
from hedron.type_authoring.depends import as_fastapi_depends
from hedron_core.diagnostics import HedronError
from hedron_core.lifetime import compile_fastapi_scope, forbid_background_capture


def setup_function() -> None:
    reset_049()


def test_hedron_names_compile_to_fastapi_scopes() -> None:
    assert compile_fastapi_scope(DependencyLifetime.HANDLER) == "function"
    assert compile_fastapi_scope(DependencyLifetime.RESPONSE) == "request"
    dep = as_fastapi_depends(DependsOn("db", lifetime=DependencyLifetime.HANDLER))
    assert dep.scope == "function"
    stream = as_fastapi_depends(
        DependsOn("db", lifetime=DependencyLifetime.RESPONSE, streaming=True)
    )
    assert stream.scope == "request"


def test_user_authored_depends_remain_valid() -> None:
    from fastapi import Depends

    def provider() -> str:
        return "ok"

    app = FastAPI()

    @app.get("/ping")
    def ping(value: str = Depends(provider)) -> dict[str, str]:
        return {"value": value}

    with TestClient(app) as client:
        assert client.get("/ping").json() == {"value": "ok"}


def test_background_capture_is_forbidden() -> None:
    try:
        forbid_background_capture(("database",))
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0001"
    else:
        raise AssertionError("expected diagnostic")


def test_streaming_helpers_remain_response_lifetime() -> None:
    plan = DependsOn("sse", lifetime=DependencyLifetime.RESPONSE, streaming=True).plan()
    assert plan.lifetime is DependencyLifetime.RESPONSE
    assert inspect.signature(SseResponse.__init__)
    app = make_app()

    @app.refreshable("/plain")
    def plain():
        return Text("ok")

    assert plain.path.endswith("/plain")


def test_397_streaming_without_response_lifetime_fail_closes() -> None:
    try:
        as_fastapi_depends(DependsOn("sse", streaming=True))
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0001"
    else:
        raise AssertionError("streaming DependsOn must require RESPONSE lifetime")
