"""Media session transport contracts."""

from __future__ import annotations

import pytest

from hedron_core.media_session import MediaChunk, MediaSession, MediaSessionState


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
