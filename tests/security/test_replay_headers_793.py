"""Regression coverage for replayed response headers (#793)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from starlette.requests import Request
from starlette.responses import RedirectResponse

from hedron import Hedron, Text


def test_replayed_action_preserves_redirect_and_application_headers() -> None:
    app = Hedron(security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/save", method="POST", idempotency="required")
    def save(_request: Request) -> RedirectResponse:
        response = RedirectResponse("/done", status_code=303)
        response.headers["HX-Redirect"] = "/done"
        response.headers["X-Receipt"] = "receipt-123"
        return response

    client = TestClient(app, follow_redirects=False)
    csrf = client.get("/").cookies["hedron_csrf"]
    headers = {"Idempotency-Key": "same-key", "X-CSRF-Token": csrf}

    first = client.post("/save", headers=headers)
    replay = client.post("/save", headers=headers)

    assert first.status_code == replay.status_code == 303
    assert first.headers["location"] == replay.headers["location"] == "/done"
    assert first.headers["hx-redirect"] == replay.headers["hx-redirect"] == "/done"
    assert first.headers["x-receipt"] == replay.headers["x-receipt"] == "receipt-123"
    assert replay.headers["hedron-replay"] == "true"


def test_memory_replay_store_round_trips_duplicate_headers() -> None:
    from hedron.replay import MemoryReplayStore, ReplayState

    store = MemoryReplayStore()
    claim = store.claim(key="k", fingerprint="fp", scope="s", retention_seconds=60)
    assert claim.state is ReplayState.FIRST
    headers = (("set-cookie", "a=1; Path=/"), ("set-cookie", "b=2; Path=/"))
    assert store.complete(
        key="k",
        scope="s",
        fingerprint="fp",
        status=200,
        body=b"ok",
        headers=headers,
    )
    replay = store.claim(key="k", fingerprint="fp", scope="s", retention_seconds=60)
    assert replay.state is ReplayState.REPLAYED
    assert replay.cached_headers == headers


def test_existing_custom_replay_store_signature_remains_compatible() -> None:
    from hedron.replay import MemoryReplayStore, ReplayOutcome

    class ExistingCustomStore:
        def __init__(self) -> None:
            self.inner = MemoryReplayStore()

        def claim(
            self,
            *,
            key: str,
            fingerprint: str,
            scope: str,
            retention_seconds: int,
        ) -> ReplayOutcome:
            return self.inner.claim(
                key=key,
                fingerprint=fingerprint,
                scope=scope,
                retention_seconds=retention_seconds,
            )

        def complete(
            self,
            *,
            key: str,
            scope: str,
            fingerprint: str,
            status: int,
            body: bytes,
            media_type: str | None = None,
        ) -> bool:
            return self.inner.complete(
                key=key,
                scope=scope,
                fingerprint=fingerprint,
                status=status,
                body=body,
                media_type=media_type,
            )

        def abort(self, *, key: str, scope: str, fingerprint: str) -> None:
            self.inner.abort(key=key, scope=scope, fingerprint=fingerprint)

    calls: list[str] = []
    app = Hedron(security="standard", explorer="off", session_secret="test-secret")
    app.state.hedron_replay_store = ExistingCustomStore()

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/charge", method="POST", idempotency="required")
    def charge(_request: Request) -> Text:
        calls.append("charged")
        return Text("charged")

    client = TestClient(app)
    csrf = client.get("/").cookies["hedron_csrf"]
    headers = {"Idempotency-Key": "same-key", "X-CSRF-Token": csrf}

    first = client.post("/charge", headers=headers)
    replay = client.post("/charge", headers=headers)

    assert first.status_code == replay.status_code == 200
    assert replay.headers["Hedron-Replay"] == "true"
    assert calls == ["charged"]
