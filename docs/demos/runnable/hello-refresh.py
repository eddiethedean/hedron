import os
from datetime import datetime, timezone

from hedron import Hedron, Page, Stack, Text, ToastHost, html

app = Hedron(
    title="Hedron App",
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
    from hedron import refresh

    return refresh(status).toast("Refreshed")


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Hello from hedron new"),
            status(),
            status.refresh_button("Refresh status"),
            ping.button("Ping"),
            ToastHost(),
        ),
        title="Home",
    )
