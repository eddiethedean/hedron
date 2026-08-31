"""Media session transport contracts."""

from __future__ import annotations

import pytest

from hedron_core.media_session import (
    MediaChunk,
    MediaSession,
    MediaSessionBudget,
    MediaSessionState,
)


def test_media_session_requires_permission() -> None:
    session = MediaSession(session_id="s1", kind="audio", origin="https://app.test")
    chunk = MediaChunk(sequence=1, content_type="audio/webm", data=b"abc", timestamp_ms=0)
    with pytest.raises(PermissionError):
        session.accept_chunk(chunk)
    session.grant()
    session.accept_chunk(chunk)
    assert session.chunks_received == 1
    session.teardown()
    assert session.state is MediaSessionState.CLOSED


def test_media_session_enforces_cadence() -> None:
    session = MediaSession(
        session_id="s2",
        kind="audio",
        origin="https://app.test",
        budget=MediaSessionBudget(cadence_ms=100, max_bandwidth_bytes_per_second=1_000_000),
    )
    session.grant()
    session.accept_chunk(MediaChunk(1, "audio/webm", b"abc", timestamp_ms=0))
    with pytest.raises(ValueError, match="cadence"):
        session.accept_chunk(MediaChunk(2, "audio/webm", b"abc", timestamp_ms=50))
    session.accept_chunk(MediaChunk(2, "audio/webm", b"abc", timestamp_ms=150))


def test_media_session_enforces_duration() -> None:
    session = MediaSession(
        session_id="s3",
        kind="audio",
        origin="https://app.test",
        budget=MediaSessionBudget(max_duration_seconds=1.0, cadence_ms=0),
    )
    session.grant()
    session.accept_chunk(MediaChunk(1, "audio/webm", b"a", timestamp_ms=0))
    with pytest.raises(RuntimeError, match="max_duration"):
        session.accept_chunk(MediaChunk(2, "audio/webm", b"a", timestamp_ms=2000))


def test_media_session_enforces_bandwidth() -> None:
    session = MediaSession(
        session_id="s4",
        kind="audio",
        origin="https://app.test",
        budget=MediaSessionBudget(
            cadence_ms=0,
            max_bandwidth_bytes_per_second=10,
        ),
    )
    session.grant()
    session.accept_chunk(MediaChunk(1, "audio/webm", b"12345", timestamp_ms=0))
    session.accept_chunk(MediaChunk(2, "audio/webm", b"12345", timestamp_ms=1))
    with pytest.raises(RuntimeError, match="max_bandwidth"):
        session.accept_chunk(MediaChunk(3, "audio/webm", b"12345", timestamp_ms=2))


def test_media_session_rejects_duplicate_sequence_and_wrong_media_type() -> None:
    session = MediaSession(session_id="s5", kind="audio", origin="https://app.test")
    session.grant()
    session.accept_chunk(MediaChunk(1, "audio/webm", b"a", timestamp_ms=0))
    with pytest.raises(ValueError, match="sequence"):
        session.accept_chunk(MediaChunk(1, "audio/webm", b"b", timestamp_ms=1000))
    with pytest.raises(ValueError, match="content_type"):
        session.accept_chunk(MediaChunk(2, "video/webm", b"b", timestamp_ms=1000))


def test_media_session_rejects_reversed_timestamp() -> None:
    session = MediaSession(session_id="s6", kind="audio", origin="https://app.test")
    session.grant()
    session.accept_chunk(MediaChunk(1, "audio/webm", b"a", timestamp_ms=100))
    with pytest.raises(ValueError, match="precedes"):
        session.accept_chunk(MediaChunk(2, "audio/webm", b"b", timestamp_ms=99))


@pytest.mark.parametrize(
    "kwargs",
    [
        {"max_duration_seconds": float("nan")},
        {"max_duration_seconds": float("inf")},
        {"cadence_ms": -1},
        {"max_chunks": 0},
    ],
)
def test_media_session_budget_rejects_invalid_values(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        MediaSessionBudget(**kwargs)  # type: ignore[arg-type]
