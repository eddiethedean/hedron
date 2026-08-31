"""Focused streaming primitives."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from hedron.streaming import stream_chunked_list, stream_tokens
from hedron_core.streaming import ChunkedList, StreamBudget, StreamedDocument, TokenStream


def test_chunked_list_respects_budget() -> None:
    source = ChunkedList(
        items=list(range(100)),
        region_id="items",
        item_html=lambda item, index: f"<li>{item}</li>",
        budget=StreamBudget(max_chunks=3, deadline_seconds=None),
        fallback_html='<div id="items">loading</div>',
    )
    chunks = list(source.iter_chunks())
    assert len(chunks) == 3
    response = stream_chunked_list(
        ChunkedList(
            items=list(range(3)),
            region_id="items",
            item_html=lambda item, index: f"<li>{item}</li>",
            budget=StreamBudget(max_chunks=3, deadline_seconds=None),
            fallback_html='<div id="items">loading</div>',
        )
    )
    assert response.headers["X-Hedron-Stream-Region"] == "items"
    assert response.headers["X-Hedron-Stream-Fallback"] == "1"

    app = FastAPI()

    @app.get("/stream")
    def _stream():
        return response

    with TestClient(app) as client:
        body = client.get("/stream").content
    assert body.startswith(b'<div id="items">loading</div>')
    assert b"<li>0</li>" in body


def test_streamed_document_metadata_first() -> None:
    doc = StreamedDocument(
        chunks=["a", "b"],
        region_id="doc",
        metadata_preamble="<!--meta-->",
        budget=StreamBudget(deadline_seconds=None),
    )
    phases = list(doc.iter_phases())
    assert phases[0] == ("metadata", "<!--meta-->")
    assert phases[1][0] == "body"


def test_token_stream_chunks() -> None:
    stream = TokenStream(
        tokens=["hel", "lo", " ", "world"],
        region_id="chat",
        budget=StreamBudget(max_chunks=10, deadline_seconds=None),
        join_with="",
    )
    chunks = list(stream.iter_chunks())
    assert "".join(chunks) == "hello world"
    response = stream_tokens(stream)
    assert response.headers["X-Hedron-Stream-Region"] == "chat"
    assert response.media_type == "text/html"


def test_chunk_delay_is_honored() -> None:
    import time

    source = ChunkedList(
        items=[1, 2],
        region_id="items",
        item_html=lambda item, index: f"<li>{item}</li>",
        budget=StreamBudget(max_chunks=10, deadline_seconds=None, chunk_delay_seconds=0.05),
    )
    started = time.monotonic()
    list(source.iter_chunks())
    assert time.monotonic() - started >= 0.04


@pytest.mark.parametrize(
    "kwargs",
    [
        {"deadline_seconds": float("nan")},
        {"deadline_seconds": float("inf")},
        {"max_chunks": 0},
        {"chunk_delay_seconds": float("nan")},
    ],
)
def test_stream_budget_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        StreamBudget(**kwargs)  # type: ignore[arg-type]
