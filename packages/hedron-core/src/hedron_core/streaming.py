"""Focused streaming primitives (phase 0.10). Ordinary render stays non-streaming."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator, Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "ChunkedList",
    "StreamBudget",
    "StreamedDocument",
    "TokenStream",
    "async_token_chunks",
    "bounded_token_chunks",
]


@dataclass(frozen=True, slots=True)
class StreamBudget:
    """Resource bounds for a focused stream."""

    max_chunks: int = 10_000
    max_chars: int = 2_000_000
    deadline_seconds: float | None = 60.0
    chunk_delay_seconds: float = 0.0


@dataclass(slots=True)
class ChunkedList:
    """Yield HTML list-item chunks for a bounded collection."""

    items: Sequence[Any]
    region_id: str
    item_html: Callable[[Any, int], str]
    budget: StreamBudget = field(default_factory=StreamBudget)
    fallback_html: str = ""

    def iter_chunks(self) -> Iterator[str]:
        started = time.monotonic()
        total_chars = 0
        for index, item in enumerate(self.items):
            if index >= self.budget.max_chunks:
                break
            if (
                self.budget.deadline_seconds is not None
                and time.monotonic() - started > self.budget.deadline_seconds
            ):
                break
            chunk = self.item_html(item, index)
            total_chars += len(chunk)
            if total_chars > self.budget.max_chars:
                break
            yield chunk

    def fallback(self) -> str:
        return (
            self.fallback_html or f'<div id="{self.region_id}" data-hedron-stream="fallback"></div>'
        )


@dataclass(slots=True)
class StreamedDocument:
    """Yield document body chunks after an optional metadata preamble."""

    chunks: Sequence[str]
    region_id: str
    metadata_preamble: str = ""
    budget: StreamBudget = field(default_factory=StreamBudget)

    def iter_phases(self) -> Iterator[tuple[str, str]]:
        """Yield (phase, html) where phase is 'metadata' then 'body'."""
        if self.metadata_preamble:
            yield ("metadata", self.metadata_preamble)
        started = time.monotonic()
        total = 0
        for index, chunk in enumerate(self.chunks):
            if index >= self.budget.max_chunks:
                break
            if (
                self.budget.deadline_seconds is not None
                and time.monotonic() - started > self.budget.deadline_seconds
            ):
                break
            total += len(chunk)
            if total > self.budget.max_chars:
                break
            yield ("body", chunk)


@dataclass(slots=True)
class TokenStream:
    """Bounded token/generator stream for chat-style output."""

    tokens: Sequence[str]
    region_id: str
    budget: StreamBudget = field(
        default_factory=lambda: StreamBudget(max_chunks=50_000, max_chars=500_000)
    )
    join_with: str = ""

    def iter_chunks(self) -> Iterator[str]:
        yield from bounded_token_chunks(
            self.tokens,
            budget=self.budget,
            join_with=self.join_with,
        )


def bounded_token_chunks(
    tokens: Sequence[str],
    *,
    budget: StreamBudget,
    join_with: str = "",
    max_chunk_tokens: int = 8,
) -> Iterator[str]:
    started = time.monotonic()
    total_chars = 0
    buffer: list[str] = []
    chunks_emitted = 0
    for token in tokens:
        if chunks_emitted >= budget.max_chunks:
            break
        if (
            budget.deadline_seconds is not None
            and time.monotonic() - started > budget.deadline_seconds
        ):
            break
        buffer.append(token)
        if len(buffer) >= max_chunk_tokens:
            chunk = join_with.join(buffer)
            total_chars += len(chunk)
            if total_chars > budget.max_chars:
                break
            yield chunk
            chunks_emitted += 1
            buffer.clear()
    if buffer and chunks_emitted < budget.max_chunks:
        chunk = join_with.join(buffer)
        if total_chars + len(chunk) <= budget.max_chars:
            yield chunk


async def async_token_chunks(
    tokens: AsyncIterator[str],
    *,
    budget: StreamBudget,
    join_with: str = "",
    max_chunk_tokens: int = 8,
) -> AsyncIterator[str]:
    started = time.monotonic()
    total_chars = 0
    buffer: list[str] = []
    chunks_emitted = 0
    async for token in tokens:
        if chunks_emitted >= budget.max_chunks:
            break
        if (
            budget.deadline_seconds is not None
            and time.monotonic() - started > budget.deadline_seconds
        ):
            break
        buffer.append(token)
        if len(buffer) >= max_chunk_tokens:
            chunk = join_with.join(buffer)
            total_chars += len(chunk)
            if total_chars > budget.max_chars:
                break
            yield chunk
            chunks_emitted += 1
            buffer.clear()
    if buffer and chunks_emitted < budget.max_chunks:
        chunk = join_with.join(buffer)
        if total_chars + len(chunk) <= budget.max_chars:
            yield chunk
