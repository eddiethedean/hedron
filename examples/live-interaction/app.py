"""First-party live interaction sample (poll, stream, SSE, jobs, WS, preload).

Polling remains the Supported production fallback on every host. SSE / streaming /
WebSocket / preload demos import from ``hedron.experimental``.
"""

from __future__ import annotations

import threading
import time
from datetime import UTC, datetime

from fastapi import Request, WebSocket
from fastapi.responses import HTMLResponse

from hedron import (
    FragmentRegion,
    Hedron,
    Link,
    Page,
    Poll,
    Stack,
    Text,
    html,
)
from hedron.experimental import (
    NavigationPreloadPolicy,
    accept_page_session_channel,
    apply_preload_headers,
    evaluate_preload_request,
    job_status_sse_response,
    sse_response,
    stream_tokens,
)
from hedron.jobs import enqueue_durable
from hedron_core.channel import PageSessionChannel
from hedron_core.component import Component
from hedron_core.jobs import InMemoryJobBackend, JobState, set_job_backend
from hedron_core.live import SseEvent
from hedron_core.models import Props
from hedron_core.prepare import PrepareContext
from hedron_core.streaming import TokenStream

app = Hedron(
    title="Hedron live interaction",
    security="standard",
    session_secret="live-interaction-dev-only",
)

_backend = InMemoryJobBackend()
set_job_backend(_backend)

ANSWER = FragmentRegion(id="answer", selector="#answer", description="Streamed answer")
_channel = PageSessionChannel(
    channel_id="live-demo",
    declared_regions=frozenset({"clock", "answer"}),
)
_preload = NavigationPreloadPolicy(enabled=True, max_concurrent=2)


class _BannerProps(Props):
    pass


class PreparedBanner(Component[_BannerProps]):
    """Tiny 0.13 prepare() demo — loads before sync render."""

    props_type = _BannerProps

    def __init__(self) -> None:
        super().__init__(_BannerProps())
        self._message = "preparing…"

    async def prepare(self, ctx: PrepareContext) -> None:
        self._message = await ctx.cached("banner", lambda: "Prepared concurrently (0.13)")

    def render(self) -> Text:
        return Text(self._message)


def clock_text() -> Text:
    now = datetime.now(UTC).strftime("%H:%M:%S UTC")
    return Text(now)


def _complete_demo_job(job_id: str) -> None:
    """Tiny in-process worker so Job SSE reaches a terminal state."""
    time.sleep(0.4)
    _backend.mark(job_id, JobState.RUNNING)
    time.sleep(0.4)
    _backend.mark(job_id, JobState.SUCCEEDED, result={"ok": True})


@app.view("/clock")
def clock():
    return clock_text()


@app.page("/")
def home() -> Page:
    job_id = enqueue_durable("demo", {"n": 1})
    threading.Thread(target=_complete_demo_job, args=(job_id,), daemon=True).start()
    return Page(
        Stack(
            PreparedBanner(),
            Text("Server time (polls every 2s)"),
            Poll(
                ref=clock.ref,
                interval_ms=2000,
                target_id=clock.dom_id,
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
            Text("SSE ping — open /sse/ping"),
            html.code("/sse/ping"),
            Text(f"Job SSE — open /jobs/{job_id}/events (demo job completes in ~1s)"),
            html.code(f"/jobs/{job_id}/events"),
            Text("WebSocket page channel — connect to /ws/page (see guide)"),
            html.code("/ws/page"),
            Text("Preload-enabled next page — /next"),
            Link("Next (preload)", href="/next"),
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


@app.get("/jobs/{job_id}/events")
def job_events(job_id: str, request: Request):
    return job_status_sse_response(
        job_id,
        backend=_backend,
        request=request,
        poll_interval_seconds=0.15,
    )


@app.websocket("/ws/page")
async def page_socket(websocket: WebSocket):
    await accept_page_session_channel(
        websocket,
        _channel,
        allowed_origins=frozenset({"http://127.0.0.1:8000", "http://localhost:8000"}),
    )


@app.page("/next")
def next_page(request: Request):
    decision = evaluate_preload_request(request, _preload)
    response = HTMLResponse(
        "<!doctype html><title>Next</title><p>Next page (preload headers applied).</p>"
    )
    return apply_preload_headers(response, decision)
