import os
from datetime import UTC, datetime

from hedron import Hedron, Page, RefreshButton, Stack, Text, html, swap

app = Hedron(
    title="HTMX interactions",
    security="standard",
    explorer="off",
    session_secret=os.environ.get("HEDRON_SESSION_SECRET", "dev-only"),
)

status = app.region("hx-guide-status", description="Status panel")
notes = app.region("hx-guide-notes", description="Notes counter")
probe = app.region("hx-guide-probe", description="Allowlist probe")


def status_panel():
    stamp = datetime.now(UTC).strftime("%H:%M:%S")
    return html.div(
        html.strong("Service healthy"),
        html.span(f"Checked at {stamp}"),
        id=status.id,
        role="status",
        aria={"live": "polite"},
    )


def notes_panel():
    return html.div(
        Text("Sample notes region"),
        html.span("Allowlisted #hx-guide-notes — count stays 0 in this example"),
        id=notes.id,
        role="status",
        aria={"live": "polite"},
    )


def probe_panel():
    return html.div(
        html.strong("Allowlisted swap"),
        html.span("HX-Target matched the declared probe region"),
        id=probe.id,
        role="status",
        aria={"live": "polite"},
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            status_panel(),
            RefreshButton.for_region(status, href="/status", label="Refresh status"),
            notes_panel(),
            RefreshButton.for_region(notes, href="/notes-count", label="Refresh sample region"),
            html.div(
                html.button(
                    "Correct target → 200",
                    type="button",
                    **{
                        "hx-get": "/probe",
                        "hx-target": probe.selector,
                        "hx-swap": "outerHTML",
                    },
                ),
                html.button(
                    "Wrong #panel → 403",
                    type="button",
                    **{
                        "hx-get": "/probe",
                        "hx-target": "#panel",
                        "hx-swap": "outerHTML",
                    },
                ),
                probe_panel(),
            ),
        ),
        title="HTMX",
    )


@app.fragment("/status", region=status)
def refresh_status():
    return swap(status_panel())


@app.fragment("/notes-count", region=notes)
def refresh_notes():
    return swap(notes_panel())


@app.fragment("/probe", region=probe)
def refresh_probe():
    return swap(probe_panel())
