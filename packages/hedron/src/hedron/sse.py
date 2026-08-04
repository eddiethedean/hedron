"""FastAPI SSE helpers (phase 0.10)."""

from __future__ import annotations

import time
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
        for key, value in hdrs.items():
            if any(ord(ch) < 32 for ch in value):
                raise ValueError(f"{key} must not contain control characters")
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
    poll_interval_seconds: float | None = None,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> SseResponse:
    """Stream job status events until terminal; polling remains a Supported fallback.

    Honors ``Last-Event-ID`` by skipping already-delivered event ids. Emits only when
    ``state`` / ``updated_at`` change. Stops when the job is terminal or missing.

    When the stored job has ``auth_subject`` / ``tenant_id`` set, the matching kwargs
    must be provided and equal or the stream ends with an authorization error event.
    """
    store = backend or get_job_backend()

    def _html(status: Any) -> str:
        if html_message is not None:
            return html_message(status)
        from hedron_core.builtins import Status

        result = render(Status(f"Job {status.job_id}: {status.state.value}", live=True))
        return result.html

    def _authorized(status: Any) -> bool:
        subject_ok = status.auth_subject is None or status.auth_subject == auth_subject
        tenant_ok = status.tenant_id is None or status.tenant_id == tenant_id
        return subject_ok and tenant_ok

    def _gen() -> Iterator[bytes]:
        last_id: str | None = None
        if request is not None:
            last_id = request.headers.get("last-event-id")
        last_emitted_key: tuple[str, float] | None = None
        while True:
            status = store.get(job_id)
            if status is None:
                yield encode_sse(
                    SseEvent(data="not-found", event="error", id=last_id or job_id)
                ).encode("utf-8")
                return
            if not _authorized(status):
                yield encode_sse(
                    SseEvent(data="forbidden", event="error", id=last_id or job_id)
                ).encode("utf-8")
                return
            event_id = f"{status.job_id}:{status.updated_at}"
            # Resume: skip the snapshot already acknowledged by the client.
            if last_id is not None and event_id == last_id and last_emitted_key is None:
                if status.state in _TERMINAL:
                    # Re-emit terminal frames so reconnecting clients still close cleanly.
                    for event in job_status_sse_events(
                        job_id=status.job_id,
                        state=status.state.value,
                        message_html=_html(status),
                        event_id=event_id,
                        retry_ms=max(1000, int(status.retry_after) * 1000),
                        terminal=True,
                    ):
                        yield encode_sse(event).encode("utf-8")
                    return
                interval = (
                    poll_interval_seconds
                    if poll_interval_seconds is not None
                    else max(0.05, float(status.retry_after))
                )
                time.sleep(interval)
                last_id = None  # only skip the first matching snapshot
                continue
            key = (status.state.value, status.updated_at)
            if key == last_emitted_key:
                if status.state in _TERMINAL:
                    return
                interval = (
                    poll_interval_seconds
                    if poll_interval_seconds is not None
                    else max(0.05, float(status.retry_after))
                )
                time.sleep(interval)
                continue
            terminal = status.state in _TERMINAL
            for event in job_status_sse_events(
                job_id=status.job_id,
                state=status.state.value,
                message_html=_html(status),
                event_id=event_id,
                retry_ms=max(1000, int(status.retry_after) * 1000),
                terminal=terminal,
            ):
                yield encode_sse(event).encode("utf-8")
            last_emitted_key = key
            last_id = None
            if terminal:
                return
            interval = (
                poll_interval_seconds
                if poll_interval_seconds is not None
                else max(0.05, float(status.retry_after))
            )
            time.sleep(interval)

    return SseResponse(_gen())
