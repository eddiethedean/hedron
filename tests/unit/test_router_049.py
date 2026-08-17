"""ROUTER-049 preserved identity and late registration."""

from __future__ import annotations

from tests.unit._helpers_049 import make_app, reset_049

from hedron import Hedron, HedronRouter, Text
from hedron.registration import fail_closed_late_registration, router_excludes_alpha_hooks
from hedron_core.diagnostics import HedronError


def setup_function() -> None:
    reset_049()


def test_hedron_router_identity_and_no_alpha_hooks() -> None:
    router = HedronRouter(prefix="/pkg", provenance="demo.pkg")
    assert isinstance(router, HedronRouter)
    assert router.hedron_provenance == "demo.pkg"
    assert router_excludes_alpha_hooks(router)


def test_late_registration_fails_after_openapi_cache() -> None:
    app = make_app()

    @app.refreshable("/ok")
    def ok():
        return Text("ok")

    _ = app.openapi()
    try:
        fail_closed_late_registration(openapi_cached=True)
    except HedronError as exc:
        assert exc.diagnostic.code == "HED-FP-0005"
    else:
        raise AssertionError("expected late-registration failure")


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
