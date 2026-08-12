"""Reference app using one HedronWorkbench object locally and on Workbench."""

from __future__ import annotations

import os
import secrets
from datetime import UTC, datetime

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
    title="Workbench facade reference",
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
            Text("Hello from Hedron on Workbench"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
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
    return Page(Text("Workbench login target"), title="Login")


@app.page("/invites/accept", name="accept_invite")
def accept_invite() -> Page:
    return Page(Text("Invite accepted"), title="Invite")


@app.get("/invite-link", include_in_schema=False)
def invite_link() -> JSONResponse:
    durable_error = ""
    try:
        app.external_url_for("accept_invite", query={"token": "smoke token +"})
    except ValueError as exc:
        durable_error = str(exc)
    return JSONResponse(
        {
            "browser_url": app.browser_url_for(
                "accept_invite",
                query={"token": "smoke token +"},
            ),
            "durable_error": durable_error,
            "capabilities": app.deployment_capabilities().as_dict(),
        }
    )


@app.page("/encoded")
def encoded_target() -> Page:
    return Page(Text("Encoded Workbench target normalized"), title="Encoded target")


@app.page("/go")
def go():
    # Deliberately return an unmounted safe redirect. The outer adapter must
    # scope Location exactly once.
    return redirect_local("/login")


@app.get("/workbench-status", include_in_schema=False)
def workbench_status() -> JSONResponse:
    """Reference-only redacted diagnostic endpoint used by the smoke matrix."""
    return JSONResponse(app.workbench_status())


@app.websocket("/ws")
async def websocket_smoke(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_text("native-ws")
    await websocket.close()
