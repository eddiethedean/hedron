"""Phase 0.18 RECORD-018: InteractionRecorder redaction."""

from __future__ import annotations

from hedron import InteractionRecorder


def test_recorder_public_only_and_redacts_secrets() -> None:
    rec = InteractionRecorder()
    rec.declare_public("POST:/api/predict")
    assert (
        rec.record(
            method="POST",
            path="/api/private",
            headers={"Authorization": "Bearer secret-token"},
            body={"password": "x", "text": "hi"},
        )
        is None
    )
    exchange = rec.record(
        method="POST",
        path="/api/predict",
        headers={"Authorization": "Bearer secret-token", "Content-Type": "application/json"},
        body={"password": "x", "text": "hi"},
        session_assumptions=("authenticated session cookie",),
        file_fixtures=("sample.png",),
    )
    assert exchange is not None
    assert exchange.headers["Authorization"] == "[redacted]"
    assert exchange.body is not None
    assert exchange.body["password"] == "[redacted]"
    assert exchange.body["text"] == "hi"

    snippets = rec.snippets()
    assert any(s.language == "python" for s in snippets)
    assert any(s.language == "http" for s in snippets)
    joined = "\n".join(s.content for s in snippets)
    assert "Bearer secret-token" not in joined
    assert "password" in joined  # key may appear but value redacted
    assert "secret-token" not in joined
    assert any("does not expand endpoint authority" in w for s in snippets for w in s.warnings)
