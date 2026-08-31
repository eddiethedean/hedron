"""Regression coverage for replay identity isolation (#792)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from starlette.authentication import AuthCredentials, AuthenticationBackend, SimpleUser
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request

from hedron import Hedron, Text
from hedron.security.policy import SecurityPolicy


def _anonymous_app(calls: list[str]) -> Hedron:
    app = Hedron(security="standard", explorer="off", session_secret="test-secret")

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/receipt", method="POST", idempotency="required")
    def receipt(request: Request) -> Text:
        client = request.headers["x-client"]
        calls.append(client)
        return Text(f"private receipt for {client}")

    return app


def test_anonymous_replay_isolated_by_csrf_cookie() -> None:
    calls: list[str] = []
    app = _anonymous_app(calls)
    alice = TestClient(app)
    bob = TestClient(app)
    alice_csrf = alice.get("/").cookies["hedron_csrf"]
    bob_csrf = bob.get("/").cookies["hedron_csrf"]

    headers = {"Idempotency-Key": "shared-key", "X-CSRF-Token": alice_csrf, "X-Client": "alice"}
    first = alice.post("/receipt", headers=headers)
    headers = {"Idempotency-Key": "shared-key", "X-CSRF-Token": bob_csrf, "X-Client": "bob"}
    second = bob.post("/receipt", headers=headers)

    assert first.status_code == second.status_code == 200
    assert first.text == "<p>private receipt for alice</p>"
    assert second.text == "<p>private receipt for bob</p>"
    assert "Hedron-Replay" not in second.headers
    assert calls == ["alice", "bob"]


def test_anonymous_replay_does_not_trust_csrf_header_when_disabled() -> None:
    calls: list[str] = []
    app = Hedron(
        security=SecurityPolicy(csrf_enabled=False, security_headers=False),
        explorer="off",
        session_secret="test-secret",
    )

    @app.action("/receipt", method="POST", idempotency="required")
    def receipt(request: Request) -> Text:
        client = request.headers["x-client"]
        calls.append(client)
        return Text(f"private receipt for {client}")

    alice = TestClient(app)
    bob = TestClient(app)
    shared = {"Idempotency-Key": "shared-key", "X-CSRF-Token": "caller-controlled"}

    first = alice.post("/receipt", headers={**shared, "X-Client": "alice"})
    second = bob.post("/receipt", headers={**shared, "X-Client": "bob"})

    assert first.status_code == second.status_code == 200
    assert first.text == "<p>private receipt for alice</p>"
    assert second.text == "<p>private receipt for bob</p>"
    assert "Hedron-Replay" not in second.headers
    assert calls == ["alice", "bob"]


class _SimpleUserBackend(AuthenticationBackend):
    async def authenticate(self, conn: object) -> tuple[AuthCredentials, SimpleUser]:
        del conn
        return AuthCredentials(["authenticated"]), SimpleUser("alice")


def test_starlette_simple_user_does_not_crash_replay_identity() -> None:
    app = Hedron(security="standard", explorer="off", session_secret="test-secret")
    app.add_middleware(AuthenticationMiddleware, backend=_SimpleUserBackend())

    @app.page("/")
    def home() -> Text:
        return Text("home")

    @app.action("/pay", method="POST", idempotency="required")
    def pay(request: Request) -> Text:
        return Text(f"paid for {request.user.display_name}")

    client = TestClient(app, raise_server_exceptions=False)
    csrf = client.get("/").cookies["hedron_csrf"]
    response = client.post(
        "/pay",
        headers={"Idempotency-Key": "payment-key", "X-CSRF-Token": csrf},
    )

    assert response.status_code == 200
    assert response.text == "<p>paid for alice</p>"
