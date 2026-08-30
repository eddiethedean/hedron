"""FastAPI SSE helpers (phase 0.10)."""

from __future__ import annotations

import math
from collections.abc import AsyncIterator, Callable, Iterator, Mapping

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
from starlette.requests import Request

from hedron_core.diagnostics import HedronError
from hedron_core.jobs import JobBackend, JobState, JobStatus, get_job_backend, job_authorized_http
from hedron_core.live import SseEvent, encode_sse, iter_sse_bytes, job_status_sse_events
from hedron_core.rendering import render
from hedron_core.sse_ext import parse_last_event_id

__all__ = [
    "SseResponse",
    "extension_script_tags",
    "job_status_sse_response",
    "sse_response",
]


_TERMINAL = frozenset({JobState.SUCCEEDED, JobState.FAILED, JobState.CANCELLED})
_MIN_POLL_INTERVAL_SECONDS = 0.05
_MAX_POLL_INTERVAL_SECONDS = 60.0


def _poll_interval(poll_interval_seconds: float | None, *, retry_after: float) -> float:
    """Resolve a finite next sleep interval within the progressive polling budget.

    Invalid explicit values fall back to the backend retry hint. Invalid backend
    hints use the floor, and extreme values are capped at 60 seconds.
    """
    normalized: float | None = None
    if poll_interval_seconds is not None:
        try:
            explicit = float(poll_interval_seconds)
        except (TypeError, ValueError, OverflowError):
            explicit = math.nan
        if math.isfinite(explicit) and explicit > 0:
            normalized = explicit
    if normalized is None:
        try:
            fallback = float(retry_after)
        except (TypeError, ValueError, OverflowError):
            fallback = _MIN_POLL_INTERVAL_SECONDS
        normalized = (
            fallback if math.isfinite(fallback) and fallback > 0 else _MIN_POLL_INTERVAL_SECONDS
        )
    return min(_MAX_POLL_INTERVAL_SECONDS, max(_MIN_POLL_INTERVAL_SECONDS, normalized))


def _retry_ms(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return 1000
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError):
        seconds = 1.0
    if not math.isfinite(seconds) or seconds <= 0:
        seconds = 1.0
    return int(min(_MAX_POLL_INTERVAL_SECONDS, max(1.0, seconds)) * 1000)


def _reject_header_controls(name: str, value: str) -> None:
    if any(ord(ch) < 32 for ch in name) or any(ord(ch) < 32 for ch in value):
        raise ValueError(f"{name} must not contain control characters")


class SseResponse(StreamingResponse):
    media_type = "text/event-stream"

    def __init__(
        self,
        content: Iterator[bytes] | AsyncIterator[bytes],
        *,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        hdrs = {
            **dict(headers or {}),
            "Cache-Control": "no-store",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
        for key, value in hdrs.items():
            _reject_header_controls(key, value)
        super().__init__(
            content,
            status_code=status_code,
            headers=hdrs,
            media_type=self.media_type,
            background=background,
        )


def extension_script_tags(*names: str) -> list[str]:
    from hedron_core.htmx_extensions import (
        COMPAT_DEFAULT_IDS,
        PUBLIC_ID_BY_ASSET_NAME,
        known_extensions,
        normalize_public_id,
    )

    if names:
        wanted_public = {normalize_public_id(name) for name in names}
    else:
        wanted_public = set(COMPAT_DEFAULT_IDS)
    tags: list[str] = []
    for ext in sorted(known_extensions(), key=lambda e: e.load_order):
        public_id = ext.public_id or PUBLIC_ID_BY_ASSET_NAME.get(ext.name, "")
        if public_id in wanted_public and not ext.deferred:
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
    html_message: Callable[[JobStatus], str] | None = None,
    poll_interval_seconds: float | None = None,
    auth_subject: str | None = None,
    tenant_id: str | None = None,
) -> SseResponse:
    """Stream job status events until terminal; polling remains a Supported fallback.

    Honors ``Last-Event-ID`` by skipping already-delivered event ids. Emits only when
    ``state`` / ``updated_at`` change. Stops when the job is terminal or missing.

    When the stored job has ``auth_subject`` / ``tenant_id`` set, the matching kwargs
    must be provided and equal or the helper raises 404 (same as missing) to avoid
    job-id enumeration. Unscoped jobs (no scope on the record) are never readable
    over HTTP. Missing jobs raise 404.
    """
    store = backend or get_job_backend()
    initial = store.get(job_id)
    if initial is None or not job_authorized_http(
        initial, auth_subject=auth_subject, tenant_id=tenant_id
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    def _html(status_obj: JobStatus) -> str:
        if html_message is not None:
            return html_message(status_obj)
        from hedron_core.builtins import Status

        result = render(Status(f"Job {status_obj.job_id}: {status_obj.state.value}", live=True))
        return result.html

    async def _gen() -> AsyncIterator[bytes]:
        import asyncio

        last_id: str | None = None
        if request is not None:
            raw_last_id = request.headers.get("last-event-id")
            if raw_last_id is not None:
                try:
                    last_id = parse_last_event_id(raw_last_id)
                except HedronError:
                    yield encode_sse(
                        SseEvent(data="invalid-last-event-id", event="error", id=job_id)
                    ).encode("utf-8")
                    return
        last_emitted_key: tuple[str, float] | None = None
        while True:
            status_obj = store.get(job_id)
            if status_obj is None:
                yield encode_sse(
                    SseEvent(data="not-found", event="error", id=last_id or job_id)
                ).encode("utf-8")
                return
            if not job_authorized_http(status_obj, auth_subject=auth_subject, tenant_id=tenant_id):
                yield encode_sse(
                    SseEvent(data="forbidden", event="error", id=last_id or job_id)
                ).encode("utf-8")
                return
            event_id = f"{status_obj.job_id}:{status_obj.updated_at}"
            # Resume: skip the snapshot already acknowledged by the client.
            if last_id is not None and event_id == last_id and last_emitted_key is None:
                if status_obj.state in _TERMINAL:
                    # Re-emit terminal frames so reconnecting clients still close cleanly.
                    for event in job_status_sse_events(
                        job_id=status_obj.job_id,
                        state=status_obj.state.value,
                        message_html=_html(status_obj),
                        event_id=event_id,
                        retry_ms=_retry_ms(status_obj.retry_after),
                        terminal=True,
                    ):
                        yield encode_sse(event).encode("utf-8")
                    return
                await asyncio.sleep(
                    _poll_interval(poll_interval_seconds, retry_after=status_obj.retry_after)
                )
                last_emitted_key = (status_obj.state.value, status_obj.updated_at)
                last_id = None  # only skip the first matching snapshot
                continue
            key = (status_obj.state.value, status_obj.updated_at)
            if key == last_emitted_key:
                if status_obj.state in _TERMINAL:
                    return
                await asyncio.sleep(
                    _poll_interval(poll_interval_seconds, retry_after=status_obj.retry_after)
                )
                continue
            terminal = status_obj.state in _TERMINAL
            for event in job_status_sse_events(
                job_id=status_obj.job_id,
                state=status_obj.state.value,
                message_html=_html(status_obj),
                event_id=event_id,
                retry_ms=_retry_ms(status_obj.retry_after),
                terminal=terminal,
            ):
                yield encode_sse(event).encode("utf-8")
            last_emitted_key = key
            last_id = None
            if terminal:
                return
            await asyncio.sleep(
                _poll_interval(poll_interval_seconds, retry_after=status_obj.retry_after)
            )

    return SseResponse(_gen())
