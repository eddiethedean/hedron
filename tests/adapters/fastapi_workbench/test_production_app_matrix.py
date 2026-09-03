"""Production-shaped FastAPI coverage for Workbench path and response adaptation."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from pathlib import Path

import pytest
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware
from starlette.types import Receive, Scope, Send

from fastapi_workbench.middleware import workbenchify

MOUNT = "/s/production-session/p/8456"
ORIGIN = "https://workbench.example"


class _RootPathInjector:
    """Model proxy/Uvicorn combinations that supply an ASGI root_path."""

    def __init__(
        self,
        app: Callable[[Scope, Receive, Send], Awaitable[None]],
        root_path: str,
    ) -> None:
        self.app = app
        self.root_path = root_path

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") in {"http", "websocket"}:
            scope = dict(scope)
            scope["root_path"] = self.root_path
        await self.app(scope, receive, send)


def _production_app(static_dir: Path):
    app = FastAPI(title="production matrix")
    app.add_middleware(SessionMiddleware, secret_key="test-secret", path="/")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> str:
        request.session["visits"] = int(request.session.get("visits", 0)) + 1
        return (
            f'<link rel="stylesheet" href="{request.url_for("static", path="app.css")}">'
            f'<a href="{request.url_for("openapi")}">schema</a>'
        )

    @app.get("/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/items/{item}")
    def item(item: str, request: Request) -> dict[str, object]:
        return {"item": item, "tags": request.query_params.getlist("tag")}

    @app.get("/go")
    def go() -> RedirectResponse:
        return RedirectResponse("/health?from=redirect#ready", status_code=303)

    @app.get("/htmx")
    def htmx() -> Response:
        return Response(
            headers={
                "HX-Redirect": "/health",
                "HX-Push-Url": "/items/history?tag=one",
                "HX-Location": json.dumps({"path": "/items/detail", "target": "#main"}),
            }
        )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.send_json(
            {
                "root_path": websocket.scope.get("root_path"),
                "path": websocket.scope.get("path"),
            }
        )
        await websocket.close()

    return workbenchify(
        app,
        mode="on",
        expected_mount=MOUNT,
        expected_origins=(ORIGIN,),
        owned_cookie_names=("session",),
    )


@pytest.fixture
def production_app(tmp_path: Path):
    (tmp_path / "app.css").write_text("body { color: navy; }", encoding="utf-8")
    return _production_app(tmp_path)


@pytest.mark.parametrize(
    ("request_path", "scope_root_path"),
    [
        (f"{MOUNT}/health", ""),
        (f"{MOUNT}/health", MOUNT),
        ("/health", MOUNT),
        (f"{MOUNT}/health", f"/proxy/8456{MOUNT}"),
        (f"{MOUNT}/health", f"/proxy/8456{MOUNT}/"),
        ("/health", f"/proxy/8456{MOUNT}"),
    ],
    ids=[
        "launcher-expected-mount",
        "canonical-root-path",
        "proxy-stripped-path",
        "workbench-proxy-root",
        "workbench-proxy-root-trailing-slash",
        "workbench-proxy-stripped-path",
    ],
)
def test_http_ingress_shapes_route_and_rebase_once(
    production_app: object,
    request_path: str,
    scope_root_path: str,
) -> None:
    app = (
        _RootPathInjector(production_app, scope_root_path)  # type: ignore[arg-type]
        if scope_root_path
        else production_app
    )
    client = TestClient(app)

    response = client.get(request_path)
    assert response.status_code == 200
    assert response.json() == {"ok": True}

    base = request_path.removesuffix("/health")
    redirect = client.get(f"{base}/go" if base else "/go", follow_redirects=False)
    assert redirect.status_code == 303
    assert redirect.headers["location"] == f"{MOUNT}/health?from=redirect#ready"


def test_static_openapi_sessions_and_generated_urls_are_mounted_once(
    production_app: object,
) -> None:
    client = TestClient(production_app)

    home = client.get(f"{MOUNT}/")
    assert home.status_code == 200
    assert f"http://testserver{MOUNT}/static/app.css" in home.text
    assert f"http://testserver{MOUNT}/openapi.json" in home.text
    set_cookie = home.headers["set-cookie"].lower()
    assert f"path={MOUNT}" in set_cookie
    assert f"path={MOUNT}{MOUNT}" not in set_cookie

    static = client.get(f"{MOUNT}/static/app.css")
    assert static.status_code == 200
    assert static.text == "body { color: navy; }"

    docs = client.get(f"{MOUNT}/docs")
    assert docs.status_code == 200
    assert f"url: '{MOUNT}/openapi.json'" in docs.text
    schema = client.get(f"{MOUNT}/openapi.json")
    assert schema.status_code == 200
    assert schema.json()["info"]["title"] == "production matrix"


def test_encoded_values_query_multiplicity_and_htmx_headers_survive_mounting(
    production_app: object,
) -> None:
    client = TestClient(production_app)

    item = client.get(
        f"{MOUNT}/items/report%20Q3%2Bfinal",
        params=[("tag", "a/b"), ("tag", "x+y")],
    )
    assert item.status_code == 200
    assert item.json() == {"item": "report Q3+final", "tags": ["a/b", "x+y"]}

    response = client.get(f"{MOUNT}/htmx")
    assert response.status_code == 200
    assert response.headers["hx-redirect"] == f"{MOUNT}/health"
    assert response.headers["hx-push-url"] == f"{MOUNT}/items/history?tag=one"
    assert json.loads(response.headers["hx-location"]) == {
        "path": f"{MOUNT}/items/detail",
        "target": "#main",
    }


def test_websocket_routes_under_the_session_mount(production_app: object) -> None:
    with TestClient(production_app).websocket_connect(f"{MOUNT}/ws") as websocket:
        payload = websocket.receive_json()
    assert payload == {"root_path": MOUNT, "path": f"{MOUNT}/ws"}
