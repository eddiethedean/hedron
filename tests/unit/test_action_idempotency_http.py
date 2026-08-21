"""HTTP idempotency / replay through ``@app.action`` and ``_wrap_endpoint``."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from hedron import Hedron, Text
from hedron_core.diagnostics import HedronError


def _csrf(client: TestClient) -> dict[str, str]:
    token = client.get("/").cookies.get("hedron_csrf") or ""
    return {"X-CSRF-Token": token}


def test_action_idempotency_skips_duplicate_post() -> None:
    app = Hedron(
        title="replay",
        security="standard",
        session_secret="secret-for-tests-32chars-ok!!",
        explorer="off",
    )
    calls = {"n": 0}

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/pay", methods=["POST"], idempotency="required")
    def pay() -> Text:
        calls["n"] += 1
        return Text("paid")

    client = TestClient(app)
    headers = {**_csrf(client), "Idempotency-Key": "k1"}
    first = client.post("/pay", headers=headers)
    second = client.post("/pay", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert "paid" in first.text
    assert "paid" in second.text
    assert calls["n"] == 1
    assert second.headers.get("Hedron-Replay") == "true"


def test_action_idempotency_aborts_on_handler_exception() -> None:
    app = Hedron(
        title="replay-abort",
        security="standard",
        session_secret="secret-for-tests-32chars-ok!!",
        explorer="off",
    )
    calls = {"n": 0}

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/fail", methods=["POST"], idempotency="required")
    def fail() -> Text:
        calls["n"] += 1
        raise RuntimeError("pay boom")

    client = TestClient(app, raise_server_exceptions=False)
    headers = {**_csrf(client), "Idempotency-Key": "k-fail"}
    first = client.post("/fail", headers=headers)
    second = client.post("/fail", headers=headers)
    assert first.status_code == 500
    assert second.status_code == 500
    assert calls["n"] == 2


def test_action_idempotency_required_without_key_raises() -> None:
    app = Hedron(
        title="replay-required",
        security="standard",
        session_secret="secret-for-tests-32chars-ok!!",
        explorer="off",
    )

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/need-key", methods=["POST"], idempotency="required")
    def need_key() -> Text:
        return Text("ok")

    client = TestClient(app, raise_server_exceptions=True)
    with pytest.raises(HedronError, match="HED-REPLAY-0001"):
        client.post("/need-key", headers=_csrf(client))
