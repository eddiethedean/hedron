"""FastAPI SSE helpers (phase 0.10)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterator, Mapping
from typing import Any

from fastapi.responses import StreamingResponse
from starlette.requests import Request

from hedron_core.jobs import JobBackend, JobState, get_job_backend
from hedron_core.live import SseEvent, encode_sse, iter_sse_bytes, job_status_sse_events
from hedron_core.rendering import render

__all__ = [
    "SseResponse",
    "extension_script_tags",
    "job_status_sse_response",
    "sse_response",
]


_TERMINAL = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})


class SseResponse(StreamingResponse):
    media_type = "text/event-stream"

    def __init__(
        self,
        content: Iterator[bytes] | AsyncIterator[bytes],
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        background: Any = None,
    ) -> None:
        hdrs = {
            "Cache-Control": "no-store",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            **dict(headers or {}),
        }
        super().__init__(
            content,
            status_code=status_code,
            headers=hdrs,
            media_type=self.media_type,
            background=background,
        )


def extension_script_tags(*names: str) -> list[str]:
    from hedron_core.htmx_extensions import known_extensions

    wanted = set(names) if names else {e.name for e in known_extensions() if not e.deferred}
    tags: list[str] = []
    for ext in sorted(known_extensions(), key=lambda e: e.load_order):
        if ext.name in wanted and not ext.deferred:
            tags.append(f'<script src="{ext.path}" defer></script>')
    return tags


def sse_response(events: Iterator[SseEvent] | list[SseEvent]) -> SseResponse:
    def _gen() -> Iterator[bytes]:
        yield from iter_sse_bytes(iter(events))

    return SseResponse(_gen())


def job_status_sse_response(
    job_id: str,
    *,
    backend: JobBackend | None = None,
    request: Request | None = None,
    html_message: Callable[[Any], str] | None = None,
) -> SseResponse:
    """Stream job status events until terminal; polling remains a Supported fallback."""
    store = backend or get_job_backend()

    def _html(status: Any) -> str:
        if html_message is not None:
            return html_message(status)
        from hedron_core.builtins import Status

        result = render(Status(f"Job {status.job_id}: {status.state.value}", live=True))
        return result.html

    def _gen() -> Iterator[bytes]:
        last_id: str | None = None
        if request is not None:
            last_id = request.headers.get("last-event-id")
        status = store.get(job_id)
        if status is None:
            yield encode_sse(
                SseEvent(data="not-found", event="error", id=last_id or job_id)
            ).encode("utf-8")
            return
        terminal = status.state in _TERMINAL
        for event in job_status_sse_events(
            job_id=status.job_id,
            state=status.state.value,
            message_html=_html(status),
            event_id=f"{status.job_id}:{status.updated_at}",
            retry_ms=max(1000, int(status.retry_after) * 1000),
            terminal=terminal,
        ):
            yield encode_sse(event).encode("utf-8")

    return SseResponse(_gen())
