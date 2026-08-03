"""Reference application authenticated CRUD tests."""

from __future__ import annotations

import base64
import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_APP_PATH = Path(__file__).resolve().parents[2] / "examples" / "reference-app" / "app.py"
_SPEC = importlib.util.spec_from_file_location("reference_app_http", _APP_PATH)
assert _SPEC and _SPEC.loader
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules["reference_app_http"] = _MOD
_SPEC.loader.exec_module(_MOD)


def _auth(user: str = "admin", password: str = "secret") -> dict[str, str]:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.fixture()
def hedron_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    store = _MOD.Store()
    monkeypatch.setattr(_MOD, "STORE", store)
    app = _MOD.build_hedron_app()
    return TestClient(app)


@pytest.fixture()
def plain_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    store = _MOD.Store()
    monkeypatch.setattr(_MOD, "STORE", store)
    app = _MOD.build_plain_fastapi_app()
    return TestClient(app)


def test_anonymous_rejected(hedron_client: TestClient) -> None:
    assert hedron_client.get("/").status_code == 401


def test_dashboard_authenticated(hedron_client: TestClient) -> None:
    response = hedron_client.get("/", headers=_auth())
    assert response.status_code == 200
    assert "Team Admin" in response.text
    assert "htmx.min.js" in response.text
    assert response.cookies.get("hedron_csrf")


def test_lazy_table_requires_auth(hedron_client: TestClient) -> None:
    assert hedron_client.get("/users/table").status_code == 401
    response = hedron_client.get("/users/table", headers=_auth())
    assert response.status_code == 200
    assert "Ada Lovelace" in response.text
    assert "<!DOCTYPE" not in response.text


def test_create_user_csrf_and_admin(hedron_client: TestClient) -> None:
    seeded = hedron_client.get("/", headers=_auth())
    token = seeded.cookies.get("hedron_csrf")
    assert token
    denied = hedron_client.post(
        "/users",
        headers=_auth(),
        data={"name": "New", "email": "new@example.com", "role": "member"},
    )
    assert denied.status_code == 403

    created = hedron_client.post(
        "/users",
        headers={**_auth(), "X-CSRF-Token": token},
        data={"name": "New User", "email": "new@example.com", "role": "member"},
    )
    assert created.status_code == 200
    assert "New User" in created.text

    member = hedron_client.post(
        "/users",
        headers={**_auth("member"), "X-CSRF-Token": token},
        data={"name": "Nope", "email": "nope@example.com", "role": "member"},
    )
    assert member.status_code == 403


def test_plain_fastapi_mode(plain_client: TestClient) -> None:
    response = plain_client.get("/", headers=_auth())
    assert response.status_code == 200
    assert "Team Admin" in response.text
    table = plain_client.get("/users/table", headers=_auth())
    assert "Grace Hopper" in table.text
