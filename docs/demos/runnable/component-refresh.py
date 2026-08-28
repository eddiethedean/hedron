import os
from datetime import datetime, timezone

from hedron import Hedron, Page, RefreshButton, Stack, html, swap

app = Hedron(
    title="RefreshButton demo",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

status = app.region("status-card")


def panel():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    return html.div(
        html.strong("Service healthy"),
        html.span(f"Checked at {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="RefreshButton",
    )


@app.view("/status", fragment_regions=(status,))
def refresh():
    return swap(panel())
