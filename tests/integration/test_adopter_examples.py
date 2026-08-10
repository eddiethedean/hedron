"""Regression tests for the small adopter-facing authentication and database recipes."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]


def _load_example(name: str) -> ModuleType:
    module_name = f"hedron_example_{name.replace('-', '_')}"
    path = ROOT / "examples" / name / "app.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_session_auth_wrong_password_has_visible_feedback() -> None:
    module = _load_example("session-auth")
    with TestClient(module.app) as client:
        seeded = client.get("/login")
        token = seeded.cookies.get("hedron_csrf")
        assert token

        response = client.post(
            "/login",
            data={
                "username": "ada",
                "password": "wrong",
                "csrf_token": token,
            },
        )

    assert response.status_code == 200
    assert response.url.path == "/login"
    assert response.url.query == b"error=1"
    assert "Invalid username or password" in response.text
    assert 'role="alert"' in response.text


def test_session_auth_success_and_anonymous_redirect() -> None:
    module = _load_example("session-auth")
    with TestClient(module.app) as client:
        anonymous = client.get("/", follow_redirects=False)
        assert anonymous.status_code == 303
        assert anonymous.headers["location"] == "/login"

        seeded = client.get("/login")
        token = seeded.cookies.get("hedron_csrf")
        assert token
        response = client.post(
            "/login",
            data={
                "username": "ada",
                "password": "correct-horse",
                "csrf_token": token,
            },
        )

    assert response.status_code == 200
    assert response.url.path == "/"
    assert "Signed in as ada" in response.text


def test_notes_recipe_rejects_blank_and_malformed_mutations() -> None:
    module = _load_example("notes-sqlalchemy")
    with TestClient(module.app) as client:
        seeded = client.get("/")
        token = seeded.cookies.get("hedron_csrf")
        assert token

        blank = client.post("/save", data={"body": "   ", "csrf_token": token})
        malformed = client.post(
            "/delete",
            data={"note_id": "not-an-integer", "csrf_token": token},
        )

    assert blank.status_code == 422
    assert malformed.status_code == 422


def test_model_demo_accepts_input_and_renders_prediction() -> None:
    module = _load_example("model-demo-0.18")
    with TestClient(module.app) as client:
        seeded = client.get("/")
        token = seeded.cookies.get("hedron_csrf")
        assert token
        response = client.post(
            "/predict",
            data={"text": "the kitten says meow", "csrf_token": token},
        )

    assert response.status_code == 200
    assert response.url.path == "/"
    assert "Prediction: cat" in response.text
    assert "the kitten says meow" in module.recorded_snippets()[-1]


def test_oidc_example_completes_callback_into_host_session(monkeypatch) -> None:
    monkeypatch.setenv("OIDC_ISSUER", "https://identity.example.test")
    monkeypatch.setenv("OIDC_CLIENT_ID", "client")
    monkeypatch.setenv("OIDC_CLIENT_SECRET", "secret")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret")
    module = _load_example("oidc")

    class FakeProvider:
        async def authorize_access_token(self, request):
            assert request.url.path == "/auth/callback"
            return {"userinfo": {"sub": "user-1", "name": "Ada"}}

    module.provider = FakeProvider()
    with TestClient(module.app) as client:
        response = client.get("/auth/callback")

    assert response.status_code == 200
    assert response.url.path == "/"
    assert "Signed in as Ada" in response.text
