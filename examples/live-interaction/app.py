"""First-party live interaction sample (poll, token stream, SSE).

Addresses EXAMPLES-10-001 for the Supported learning path: polling works on every
host; streaming and SSE are FastAPI-flagship. WebSocket/preload helpers remain in
the live-interaction guide for advanced use.
"""

from __future__ import annotations

from datetime import UTC, datetime

from hedron import (
    ComponentRef,
    FragmentRegion,
    Hedron,
    InteractionResult,
    Page,
    Poll,
    Stack,
    Text,
    html,
    sse_response,
    stream_tokens,
)
from hedron_core.live import SseEvent
from hedron_core.streaming import TokenStream

app = Hedron(
    title="Hedron live interaction",
    security="standard",
    session_secret="live-interaction-dev-only",
)

CLOCK = FragmentRegion(
    id="clock",
    selector="#clock",
    description="UTC clock panel",
)
CLOCK_REF = ComponentRef(
    logical_id="clock",
    path="/clock",
    target="#clock",
    swap="innerHTML",
)
ANSWER = FragmentRegion(id="answer", selector="#answer", description="Streamed answer")


def clock_text() -> Text:
    now = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return Text(now)


@app.component("/clock", fragment_regions=(CLOCK,))
def clock_fragment() -> InteractionResult:
    return InteractionResult(
        content=clock_text(),
        region_id=CLOCK.id,
        explanation="Refresh the UTC clock region",
    )


@app.page("/")
def home() -> Page:
    return Page(
        Stack(
            Text("Server time (polls every 2s)"),
            Poll(
                ref=CLOCK_REF,
                interval_ms=2000,
                target_id=CLOCK.id,
                content=clock_text(),
            ),
            Text("Streamed answer (loads on page open)"),
            html.div(
                Text("Waiting…"),
                id=ANSWER.id,
                **{
                    "hx-get": "/stream/answer",
                    "hx-trigger": "load",
                    "hx-swap": "innerHTML",
                },
            ),
            Text("SSE ping (open /sse/ping in another tab or EventSource)"),
            html.code("/sse/ping"),
        ),
        title="Live interaction",
    )


@app.get("/stream/answer")
def stream_answer():
    tokens = TokenStream(
        region_id=ANSWER.id,
        tokens=["Hello", ", ", "live", " ", "Hedron", "!"],
    )
    return stream_tokens(tokens)


@app.get("/sse/ping")
def sse_ping():
    """Minimal official SSE response for learning / proxy buffering checks."""
    return sse_response(
        [
            SseEvent(data="ping", event="message", id="1"),
            SseEvent(data="done", event="message", id="2"),
        ]
    )
