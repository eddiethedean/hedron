"""Packaged 0.48 HTMX extension declaration sample."""

from __future__ import annotations

from hedron import Hedron, Page, Stack, Text
from hedron.experimental import sse_response
from hedron_core.builtins.shell import HtmxLink
from hedron_core.live import SseEvent
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.sse_ext import SseRegion

app = Hedron(title="HTMX extensions", explorer="off", session_secret="dev-secret")


@app.page("/")
def home() -> Page:
    link = HtmxLink(
        "Preload next",
        SafeUrl.parse("/next", purpose=UrlPurpose.NAVIGATION),
        preload="mousedown",
        target="#main",
    )
    region = SseRegion(
        Text("Job events stream here. Keep a Poll control as the Supported fallback."),
        connect=SafeUrl.parse("/events", purpose=UrlPurpose.NAVIGATION),
        swap="message",
        close="hedron-close",
        id="events",
    )
    return Page(
        Stack(
            Text("Declared SSE, head-support, and GET preload. Morph is not admitted."),
            link,
            region,
        ),
        title="HTMX extensions",
        htmx_extensions=("sse", "head-support", "preload"),
    )


@app.page("/next")
def next_page() -> Page:
    return Page(Text("Preloaded GET fragment destination."), title="Next")


@app.page("/opt-out")
def opt_out() -> Page:
    return Page(Text("Zero HTMX extension bytes."), title="Opt out", htmx_extensions=())


@app.get("/events")
def events():
    return sse_response([SseEvent(data="ok", event="message", id="1")])
