"""HedronWorkbench reference app deployed as a FastAPI API on Posit Connect."""

from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime
from urllib.parse import urlsplit

from fastapi import Request, WebSocket
from starlette.responses import JSONResponse

from hedron import (
    CsrfField,
    Form,
    Page,
    RefreshButton,
    Stack,
    SubmitButton,
    Text,
    html,
    redirect_local,
    swap,
)
from hedron_workbench import HedronWorkbench

app = HedronWorkbench(
    title="Posit Connect reference",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET") or secrets.token_urlsafe(32),
)

status = app.region("service-status", description="Live status panel")


def status_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home(request: Request) -> Page:
    request.session["smoke"] = "ok"
    return Page(
        Stack(
            Text("Hello from Hedron on Connect"),
            status_panel(),
            RefreshButton.for_region(
                status,
                href="/status",
                label="Refresh status",
            ),
            Form(
                CsrfField(),
                SubmitButton("Ping"),
                action="/ping",
                method="post",
            ),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())


@app.action("/ping", method="POST")
def ping() -> Page:
    return Page(Text("pong"), title="Pong")


@app.page("/login")
def login() -> Page:
    return Page(Text("Connect login target"), title="Login")


@app.page("/invites/accept", name="accept_invite")
def accept_invite() -> Page:
    return Page(Text("Invite accepted"), title="Invite")


@app.get("/invite-link", include_in_schema=False)
def invite_link(request: Request) -> JSONResponse:
    """Exercise request-aware links that may be sent outside the browser."""
    return JSONResponse(
        {
            "url": app.external_url_for(
                "accept_invite",
                request=request,
                query={"token": "smoke token +"},
            )
        }
    )


@app.page("/go")
def go():
    return redirect_local("/login")


@app.get("/connect-scope", include_in_schema=False)
def connect_scope(request: Request) -> JSONResponse:
    base = request.headers.get("rstudio-connect-app-base-url", "")
    try:
        app.external_url("/health", request=request)
        public_base_valid = True
    except ValueError:
        public_base_valid = False
    return JSONResponse(
        {
            "posit_product": os.environ.get("POSIT_PRODUCT", ""),
            "header_present": bool(base),
            "header_count": len(request.headers.getlist("rstudio-connect-app-base-url")),
            "header_path": urlsplit(base).path if base else "",
            "root_path": str(request.scope.get("root_path") or ""),
            "request_path": str(request.scope.get("path") or ""),
            "client_host": request.client.host if request.client else "",
            "app_mount": str(app.state.hedron_mount_path or ""),
            "app_cookie_path": str(app.state.hedron_cookie_path or "/"),
            "workbench_active": app.hedron_workbench.active,
            "normalizer_count": app.workbench_status()["normalizer_count"],
            "public_base_valid": public_base_valid,
            "capabilities": app.deployment_capabilities(request=request).as_dict(),
            "server_secret_env_present": bool(
                os.environ.get("PCT_LICENSE") or os.environ.get("CONNECT_BOOTSTRAP_SECRETKEY")
            ),
        }
    )


@app.websocket("/ws")
async def websocket_smoke(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_text("native-ws")
    await websocket.close()
