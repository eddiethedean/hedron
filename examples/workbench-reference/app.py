"""Existing-style Hedron app for Workbench launch recipes. No workbench imports."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from hedron import Hedron, Page, Stack, Text, ToastHost, html, refresh

app = Hedron(
    title="Workbench reference",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.action("/ping", fallback="/")
def ping():
    return refresh(status).toast("pong")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from Hedron on Workbench"),
            status(),
            status.refresh_button("Refresh status"),
            ping.button("Ping"),
            ToastHost(),
        ),
        title="Home",
    )
