"""#378: job_status_sse_response must fail closed on invalid Last-Event-ID."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

from hedron.sse import job_status_sse_response
from hedron_core.jobs.memory import InMemoryJobBackend


def _body(raw: str) -> bytes:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, auth_subject="alice")
    request = MagicMock()
    request.headers.get.return_value = raw
    response = job_status_sse_response(
        handle.job_id,
        backend=backend,
        request=request,
        auth_subject="alice",
        poll_interval_seconds=0.01,
    )

    async def _collect() -> bytes:
        chunks: list[bytes] = []
        async for chunk in response.body_iterator:
            chunks.append(chunk if isinstance(chunk, bytes) else bytes(chunk))
        return b"".join(chunks)

    return asyncio.run(_collect())


def test_junk_and_overlong_last_event_id_fail_closed() -> None:
    for raw in ("***", "x" * 200, "<script>"):
        body = _body(raw)
        assert b"invalid-last-event-id" in body
        assert raw.encode() not in body
