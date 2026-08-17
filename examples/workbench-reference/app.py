"""Existing-style Hedron app for Workbench launch recipes. No workbench imports."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from hedron import Hedron, Page, Stack, Text, html, refresh

app = Hedron(
    title="Workbench reference",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
)


@app.refreshable("/status")
def status():
    stamp = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.command("/ping", fallback="/")
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
        ),
        title="Home",
    )
