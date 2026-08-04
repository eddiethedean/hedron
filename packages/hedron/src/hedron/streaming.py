"""Focused streaming HTTP responses (phase 0.10)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any

from fastapi.responses import StreamingResponse

from hedron_core.streaming import ChunkedList, StreamedDocument, TokenStream

__all__ = [
    "StreamingComponentResponse",
    "stream_chunked_list",
    "stream_document",
    "stream_tokens",
]


def _prefix_fallback(
    content: Iterator[bytes] | AsyncIterator[bytes],
    fallback_html: str,
) -> Iterator[bytes] | AsyncIterator[bytes]:
    fallback = fallback_html.encode("utf-8")
    if hasattr(content, "__aiter__"):

        async def _async() -> AsyncIterator[bytes]:
            yield fallback
            async for chunk in content:  # type: ignore[union-attr]
                yield chunk

        return _async()

    def _sync() -> Iterator[bytes]:
        yield fallback
        yield from content  # type: ignore[misc]

    return _sync()


class StreamingComponentResponse(StreamingResponse):
    """Stream focused HTML chunks for an addressable region."""

    media_type = "text/html"

    def __init__(
        self,
        content: Iterator[bytes] | AsyncIterator[bytes],
        *,
        region_id: str,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        background: Any = None,
        fallback_html: str | None = None,
    ) -> None:
        hdrs = {
            "Cache-Control": "no-store",
            "X-Hedron-Stream-Region": region_id,
            **dict(headers or {}),
        }
        if fallback_html is not None:
            hdrs["X-Hedron-Stream-Fallback"] = "1"
            content = _prefix_fallback(content, fallback_html)
        super().__init__(
            content,
            status_code=status_code,
            headers=hdrs,
            media_type=self.media_type,
            background=background,
        )


def stream_chunked_list(source: ChunkedList) -> StreamingComponentResponse:
    def _gen() -> Iterator[bytes]:
        for chunk in source.iter_chunks():
            yield chunk.encode("utf-8")

    return StreamingComponentResponse(
        _gen(),
        region_id=source.region_id,
        fallback_html=source.fallback(),
    )


def stream_document(source: StreamedDocument) -> StreamingComponentResponse:
    def _gen() -> Iterator[bytes]:
        for _phase, chunk in source.iter_phases():
            yield chunk.encode("utf-8")

    return StreamingComponentResponse(_gen(), region_id=source.region_id)


def stream_tokens(source: TokenStream) -> StreamingComponentResponse:
    def _gen() -> Iterator[bytes]:
        for chunk in source.iter_chunks():
            yield chunk.encode("utf-8")

    return StreamingComponentResponse(_gen(), region_id=source.region_id)
