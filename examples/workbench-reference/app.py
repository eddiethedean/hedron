"""Existing-style Hedron app for Workbench launch recipes. No workbench imports."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from hedron import (
    CsrfField,
    Form,
    Hedron,
    Page,
    RefreshButton,
    Stack,
    SubmitButton,
    Text,
    html,
    swap,
)

app = Hedron(
    title="Workbench reference",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "replace-in-production"),
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
def home() -> Page:
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
