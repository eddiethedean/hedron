"""HANDSOFF-052 evidence."""

from __future__ import annotations

from starlette.responses import RedirectResponse
from starlette.testclient import TestClient

from hedron_posit import HedronPosit, PositConfig
from hedron_posit.config import WorkbenchConfig, WorkbenchMode


def test_hands_off_enables_mount_adaptation_without_workbench() -> None:
    app = HedronPosit(
        title="handsoff-052",
        root_path="/apps/demo",
        posit=PositConfig(hands_off=True, workbench=WorkbenchConfig(mode=WorkbenchMode.OFF)),
        session_secret="test-secret-handsoff-052",
    )
    assert app.hands_off is True
    assert bool(getattr(app.state, "hedron_posit_hands_off", False)) is True
    assert app._workbench_asgi.active is True
    assert app._workbench_asgi.expected_mount == "/apps/demo"
    assert app.adapt_local_url("/profile") == "/apps/demo/profile"


def test_hands_off_rewrites_location_header_once() -> None:
    app = HedronPosit(
        title="handsoff-location",
        root_path="/apps/demo",
        posit=PositConfig(hands_off=True, workbench=WorkbenchConfig(mode=WorkbenchMode.OFF)),
        session_secret="test-secret-handsoff-loc",
    )

    @app.get("/go")
    async def go() -> RedirectResponse:
        return RedirectResponse("/login", status_code=303)

    client = TestClient(app)
    response = client.get("/go", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/apps/demo/login"


def test_hands_off_rewrites_hx_redirect_once() -> None:
    from starlette.responses import Response

    app = HedronPosit(
        title="handsoff-hx",
        root_path="/apps/demo",
        posit=PositConfig(hands_off=True, workbench=WorkbenchConfig(mode=WorkbenchMode.OFF)),
        session_secret="test-secret-handsoff-hx",
    )

    @app.get("/go")
    async def go() -> Response:
        response = Response("ok")
        response.headers["HX-Redirect"] = "/login"
        return response

    client = TestClient(app)
    response = client.get("/go")
    assert response.headers["hx-redirect"] == "/apps/demo/login"


def test_hands_off_off_by_default() -> None:
    app = HedronPosit(title="handsoff-default", session_secret="test-secret-handsoff-default")
    assert app.hands_off is False
