"""Phase 0.18 RECORD-018: InteractionRecorder redaction."""

from __future__ import annotations

from hedron import InteractionRecorder
from hedron.recorder import SENSITIVE_HEADER_NAMES


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
    # public=True cannot force-record a non-allowlisted path.
    assert (
        rec.record(
            method="POST",
            path="/api/secret",
            body={"text": "nope"},
            public=True,
        )
        is None
    )
    exchange = rec.record(
        method="POST",
        path="/api/predict",
        headers={"Authorization": "Bearer secret-token", "Content-Type": "application/json"},
        body={"password": "x", "text": "hi", "items": [{"password": "nested"}]},
        session_assumptions=("authenticated session cookie",),
        file_fixtures=("sample.png",),
    )
    assert exchange is not None
    assert exchange.headers["Authorization"] == "[redacted]"
    assert exchange.body is not None
    assert exchange.body["password"] == "[redacted]"
    assert exchange.body["text"] == "hi"
    assert exchange.body["items"][0]["password"] == "[redacted]"

    snippets = rec.snippets()
    assert any(s.language == "python" for s in snippets)
    assert any(s.language == "http" for s in snippets)
    joined = "\n".join(s.content for s in snippets)
    assert "Bearer secret-token" not in joined
    assert "password" in joined  # key may appear but value redacted
    assert "secret-token" not in joined
    assert any("does not expand endpoint authority" in w for s in snippets for w in s.warnings)


def test_recorder_redacts_every_sensitive_header_spelling_before_storage() -> None:
    rec = InteractionRecorder()
    rec.declare_public("/x")
    headers = {
        name.replace("-", "_").upper(): f"secret-{index}"
        for index, name in enumerate(sorted(SENSITIVE_HEADER_NAMES))
    }

    exchange = rec.record(method="GET", path="/x", headers=headers)

    assert exchange is not None
    assert set(exchange.headers.values()) == {"[redacted]"}
    recorded = "\n".join(snippet.content for snippet in rec.snippets())
    for value in headers.values():
        assert value not in recorded
