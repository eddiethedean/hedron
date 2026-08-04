"""Timed media chunk session transport contracts (phase 0.10). Capture UI is 0.15."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

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

    def grant(self) -> None:
        if self.state is MediaSessionState.CLOSED:
            raise RuntimeError("session already closed")
        self.permission_granted = True
        self.state = MediaSessionState.ACTIVE

    def accept_chunk(self, chunk: MediaChunk) -> None:
        if not self.permission_granted:
            raise PermissionError("media permission not granted")
        if self.state is not MediaSessionState.ACTIVE:
            raise RuntimeError(f"session not active: {self.state}")
        if len(chunk.data) > self.budget.max_chunk_bytes:
            raise ValueError("chunk exceeds max_chunk_bytes")
        if self.chunks_received >= self.budget.max_chunks:
            raise RuntimeError("max_chunks exceeded")
        self.chunks_received += 1
        self.bytes_received += len(chunk.data)

    def teardown(self, *, failed: bool = False) -> None:
        self.state = MediaSessionState.FAILED if failed else MediaSessionState.CLOSED
