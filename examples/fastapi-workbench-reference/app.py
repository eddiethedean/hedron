"""Plain FastAPI reference app for fastapi-workbench REALWB-030 / FASTAPI-030."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="FastAPI Workbench reference")
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SESSION_SECRET", "replace-me"))

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> str:
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    mount = str(request.scope.get("root_path") or "")
    ping_action = f"{mount}/ping"
    docs_href = f"{mount}/docs"
    return f"""<!doctype html>
<html><head><title>FastAPI Workbench</title></head>
<body>
  <h1>Hello from plain FastAPI on Workbench</h1>
  <p id="status">All systems operational · refreshed {stamp}</p>
  <p><a href="{docs_href}">OpenAPI docs</a></p>
  <form action="{ping_action}" method="post">
    <button type="submit">Ping</button>
  </form>
</body></html>"""


@app.post("/ping")
def ping() -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)


@app.get("/login")
def login() -> dict[str, str]:
    return {"login": "ok"}


@app.get("/go")
def go() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)


@app.get("/encoded")
def encoded_target() -> dict[str, str]:
    return {"message": "Encoded Workbench target normalized"}


@app.get("/status")
def status() -> dict[str, str]:
    return {"ok": True, "at": datetime.now(UTC).isoformat()}


@app.get("/workbench-status", include_in_schema=False)
def workbench_status(request: Request) -> dict[str, object]:
    from fastapi_workbench.config import WorkbenchConfig
    from fastapi_workbench.middleware import workbenchified_for_asgi_app
    from fastapi_workbench.redact import redact_record
    from fastapi_workbench.resolve import resolve_deployment

    resolved = resolve_deployment(WorkbenchConfig(), compatibility_aliases=False)
    payload = dict(redact_record(resolved.as_dict()))
    scope_mount = str(request.scope.get("root_path") or "")
    wrapped = workbenchified_for_asgi_app(request.app) or bool(resolved.active and scope_mount)
    payload["workbenchified"] = wrapped
    payload["normalizer_count"] = 1 if wrapped else 0
    return payload


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_text("native-ws")
    await websocket.close()
