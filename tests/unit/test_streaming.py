"""Focused streaming primitives."""

from __future__ import annotations

from hedron.streaming import stream_chunked_list, stream_tokens
from hedron_core.streaming import ChunkedList, StreamBudget, StreamedDocument, TokenStream


def test_chunked_list_respects_budget() -> None:
    source = ChunkedList(
        items=list(range(100)),
        region_id="items",
        item_html=lambda item, index: f"<li>{item}</li>",
        budget=StreamBudget(max_chunks=3, deadline_seconds=None),
    )
    chunks = list(source.iter_chunks())
    assert len(chunks) == 3
    response = stream_chunked_list(source)
    assert response.headers["X-Hedron-Stream-Region"] == "items"


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
