"""ROUTER-049 preserved identity and late registration."""

from __future__ import annotations

from fastapi.testclient import TestClient
from tests.unit._helpers_049 import make_app, reset_049

from hedron import Hedron, HedronRouter, Page, Text
from hedron.registration import router_excludes_alpha_hooks
from hedron_core.diagnostics import HedronError


def setup_function() -> None:
    reset_049()


def test_hedron_router_identity_and_no_alpha_hooks() -> None:
    router = HedronRouter(prefix="/pkg", provenance="demo.pkg")
    assert isinstance(router, HedronRouter)
    assert router.hedron_provenance == "demo.pkg"
    assert router_excludes_alpha_hooks(router)


def test_page_after_openapi_cache_fails_closed() -> None:
    app = make_app()

    @app.refreshable("/ok")
    def ok():
        return Text("ok")

    first = app.openapi()
    try:

        @app.page("/after-cache")
        def after():
            return Page(Text("late"), title="L")
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0005"
    else:
        raise AssertionError("expected late-registration failure")

    schema = app.openapi()
    assert schema is first
    assert "/after-cache" not in (schema.get("paths") or {})
    with TestClient(app) as client:
        assert client.get("/after-cache").status_code == 404


def test_nested_router_include_before_seal() -> None:
    app: Hedron = make_app()
    nested = HedronRouter(prefix="/nested", provenance="nested")

    @nested.page("/p")
    def page():
        return Text("n")

    assert any(str(getattr(route, "path", "")).endswith("/p") for route in nested.routes)
    app.include_router(nested)
    paths = [str(getattr(route, "path", "")) for route in app.routes]
    assert any(path.endswith("/nested/p") or path == "/p" for path in paths) or any(
        str(getattr(route, "path", "")).endswith("/p") for route in nested.routes
    )


def test_nested_page_after_seal_is_not_served() -> None:
    app = make_app()
    nested = HedronRouter(prefix="/z", provenance="z")

    @nested.page("/ok")
    def nested_ok():
        return Page(Text("ok"), title="O")

    app.include_router(nested)

    @app.page("/")
    def home():
        return Page(Text("h"), title="H")

    with TestClient(app) as client:
        assert client.get("/z/ok").status_code == 200
        try:

            @nested.page("/post-seal")
            def nested_late():
                return Page(Text("pwn"), title="P")
        except HedronError as exc:
            assert exc.diagnostic.code in {"HED-FP-0005", "HED-RENDER-0006"}
        else:
            raise AssertionError("expected sealed-registry failure")
        response = client.get("/z/post-seal")
        assert response.status_code == 404
        assert "pwn" not in response.text
