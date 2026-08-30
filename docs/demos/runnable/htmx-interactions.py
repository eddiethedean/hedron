import os
from datetime import datetime, timezone

from hedron import Hedron, Page, Stack, Text, html

app = Hedron(
    title="HTMX interactions",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

_NOTES: list[str] = []


@app.view("/status")
def status():
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    return html.div(
        Text(f"All systems operational · refreshed {stamp}"),
        role="status",
        aria={"live": "polite"},
    )


@app.view("/notes-count")
def notes():
    return html.div(
        Text(f"Notes saved: {len(_NOTES)}"),
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status(),
            status.refresh_button("Refresh status"),
            notes(),
            notes.refresh_button("Refresh notes count"),
        ),
        title="Home",
    )
