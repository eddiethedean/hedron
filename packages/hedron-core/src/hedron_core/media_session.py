"""Timed media chunk session transport contracts (phase 0.10). Capture UI is 0.15."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Literal

from hedron_core.compat import StrEnum

__all__ = [
    "MediaChunk",
    "MediaSession",
    "MediaSessionBudget",
    "MediaSessionState",
]


class MediaSessionState(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class MediaSessionBudget:
    max_duration_seconds: float = 60.0
    cadence_ms: int = 250
    max_chunk_bytes: int = 256_000
    max_chunks: int = 2_400
    max_bandwidth_bytes_per_second: int = 1_000_000


@dataclass(frozen=True, slots=True)
class MediaChunk:
    sequence: int
    content_type: str
    data: bytes
    timestamp_ms: int


@dataclass(slots=True)
class MediaSession:
    """Transport-only media chunk session (no capture UI)."""

    session_id: str
    kind: Literal["image", "audio", "video", "audio-out", "video-out"]
    origin: str
    permission_granted: bool = False
    state: MediaSessionState = MediaSessionState.PENDING
    budget: MediaSessionBudget = field(default_factory=MediaSessionBudget)
    chunks_received: int = 0
    bytes_received: int = 0
    fallback: Literal["upload", "poll", "none"] = "upload"
    _started_at_ms: int | None = field(default=None, repr=False)
    _last_timestamp_ms: int | None = field(default=None, repr=False)
    _window_started_monotonic: float | None = field(default=None, repr=False)
    _window_bytes: int = field(default=0, repr=False)

    def grant(self) -> None:
        if self.state is MediaSessionState.CLOSED:
            raise RuntimeError("session already closed")
        self.permission_granted = True
        self.state = MediaSessionState.ACTIVE
        self._started_at_ms = None
        self._last_timestamp_ms = None
        self._window_started_monotonic = time.monotonic()
        self._window_bytes = 0

    def accept_chunk(self, chunk: MediaChunk) -> None:
        if not self.permission_granted:
            raise PermissionError("media permission not granted")
        if self.state is not MediaSessionState.ACTIVE:
            raise RuntimeError(f"session not active: {self.state}")
        if len(chunk.data) > self.budget.max_chunk_bytes:
            raise ValueError("chunk exceeds max_chunk_bytes")
        if self.chunks_received >= self.budget.max_chunks:
            raise RuntimeError("max_chunks exceeded")

        started = self._started_at_ms
        if started is None:
            started = chunk.timestamp_ms
            self._started_at_ms = started
        elapsed_ms = chunk.timestamp_ms - started
        if elapsed_ms < 0:
            raise ValueError("chunk timestamp precedes session start")
        if elapsed_ms / 1000.0 > self.budget.max_duration_seconds:
            raise RuntimeError("max_duration_seconds exceeded")

        if self._last_timestamp_ms is not None and self.budget.cadence_ms > 0:
            delta = chunk.timestamp_ms - self._last_timestamp_ms
            if delta < self.budget.cadence_ms:
                raise ValueError("chunk cadence_ms violated")

        now = time.monotonic()
        if self._window_started_monotonic is None:
            self._window_started_monotonic = now
            self._window_bytes = 0
        window_elapsed = now - self._window_started_monotonic
        if window_elapsed >= 1.0:
            self._window_started_monotonic = now
            self._window_bytes = 0
        if self._window_bytes + len(chunk.data) > self.budget.max_bandwidth_bytes_per_second:
            raise RuntimeError("max_bandwidth_bytes_per_second exceeded")

        self._window_bytes += len(chunk.data)
        self._last_timestamp_ms = chunk.timestamp_ms
        self.chunks_received += 1
        self.bytes_received += len(chunk.data)

    def teardown(self, *, failed: bool = False) -> None:
        self.state = MediaSessionState.FAILED if failed else MediaSessionState.CLOSED
