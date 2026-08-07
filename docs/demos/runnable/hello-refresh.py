import os
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="Hedron App",
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
            Text("Hello from hedron new"),
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
        ),
        title="Home",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())
