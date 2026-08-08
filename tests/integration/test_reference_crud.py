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
def hedron_client(monkeypatch: pytest.MonkeyPatch):
    store = _MOD.Store()
    monkeypatch.setattr(_MOD, "STORE", store)
    app = _MOD.build_hedron_app()
    # strict CSP sets Secure CSRF cookies; exercise HTTPS like production.
    with TestClient(app, base_url="https://testserver") as client:
        yield client


@pytest.fixture()
def plain_client(monkeypatch: pytest.MonkeyPatch):
    store = _MOD.Store()
    monkeypatch.setattr(_MOD, "STORE", store)
    app = _MOD.build_plain_fastapi_app()
    with TestClient(app) as client:
        yield client


def test_anonymous_rejected(hedron_client: TestClient) -> None:
    assert hedron_client.get("/").status_code == 401


def test_dashboard_authenticated(hedron_client: TestClient) -> None:
    response = hedron_client.get("/", headers=_auth())
    assert response.status_code == 200
    assert "Team Admin" in response.text
    assert "htmx.min.js" in response.text
    assert "/hedron-assets/" in response.text
    assert 'rel="stylesheet"' in response.text
    assert "hedron-disclose.mjs" in response.text
    assert "hedron-ui.mjs" in response.text
    cookie = response.cookies.get("hedron_csrf")
    assert cookie
    import re

    hidden = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.text)
    assert hidden is not None
    assert hidden.group(1) == cookie
    assert cookie in response.text
    assert "X-CSRF-Token" in response.text


def test_lazy_table_requires_auth(hedron_client: TestClient) -> None:
    assert hedron_client.get("/users/table").status_code == 401
    response = hedron_client.get("/users/table", headers=_auth())
    assert response.status_code == 200
    assert "Ada Lovelace" in response.text
    assert "<!DOCTYPE" not in response.text


def test_create_user_csrf_and_admin(hedron_client: TestClient) -> None:
    import re

    seeded = hedron_client.get("/", headers=_auth())
    cookie = seeded.cookies.get("hedron_csrf")
    hidden = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', seeded.text)
    assert cookie and hidden
    token = hidden.group(1)
    assert token == cookie
    denied = hedron_client.post(
        "/users",
        headers=_auth(),
        data={"name": "New", "email": "new@example.com", "role": "member"},
    )
    assert denied.status_code == 403

    hx = {"HX-Request": "true", "HX-Target": "#user-table"}
    created = hedron_client.post(
        "/users",
        headers={**_auth(), "X-CSRF-Token": token, **hx},
        data={"name": "New User", "email": "new@example.com", "role": "member"},
    )
    assert created.status_code == 200
    assert "New User" in created.text
    assert "<!DOCTYPE" not in created.text

    # Form-field CSRF path (no header) must also succeed on the HTMX fragment path.
    form_ok = hedron_client.post(
        "/users",
        headers={**_auth(), **hx},
        data={
            "name": "Form Token",
            "email": "form@example.com",
            "role": "member",
            "csrf_token": token,
        },
    )
    assert form_ok.status_code == 200
    assert "Form Token" in form_ok.text

    member = hedron_client.post(
        "/users",
        headers={**_auth("member"), "X-CSRF-Token": token, **hx},
        data={"name": "Nope", "email": "nope@example.com", "role": "member"},
    )
    assert member.status_code == 403


def test_create_user_progressive_enhancement_redirects(hedron_client: TestClient) -> None:
    """No HX-Request → classic POST redirects to full Page (PE-019 / human AT corpus)."""
    import re

    seeded = hedron_client.get("/", headers=_auth())
    hidden = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', seeded.text)
    assert hidden
    token = hidden.group(1)
    created = hedron_client.post(
        "/users",
        headers={**_auth(), "X-CSRF-Token": token},
        data={"name": "PE User", "email": "pe@example.com", "role": "member"},
        follow_redirects=False,
    )
    assert created.status_code == 303
    location = created.headers.get("location", "")
    assert "msg=" in location
    follow = hedron_client.get(location, headers=_auth())
    assert follow.status_code == 200
    assert "<!DOCTYPE html>" in follow.text or "<html" in follow.text.lower()
    assert "PE User" in follow.text or "User created" in follow.text
    assert "Edit users" in follow.text


def test_edit_user_page_and_progressive_update(hedron_client: TestClient) -> None:
    import re

    seeded = hedron_client.get("/", headers=_auth())
    assert "Edit Grace Hopper" in seeded.text
    edit = hedron_client.get("/users/2/edit", headers=_auth())
    assert edit.status_code == 200
    assert "Update user" in edit.text
    assert "Grace Hopper" in edit.text
    hidden = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', edit.text)
    assert hidden
    token = hidden.group(1)
    updated = hedron_client.post(
        "/users/2",
        headers={**_auth(), "X-CSRF-Token": token},
        data={"name": "Grace PE", "email": "grace@example.com", "role": "member"},
        follow_redirects=False,
    )
    assert updated.status_code == 303
    follow = hedron_client.get(updated.headers["location"], headers=_auth())
    assert "Grace PE" in follow.text or "User updated" in follow.text


def test_update_and_delete_user(hedron_client: TestClient) -> None:
    seeded = hedron_client.get("/", headers=_auth())
    token = seeded.cookies.get("hedron_csrf")
    assert token
    hx = {"HX-Request": "true", "HX-Target": "#user-table"}
    updated = hedron_client.post(
        "/users/2",
        headers={**_auth(), "X-CSRF-Token": token, **hx},
        data={"name": "Grace Updated", "email": "grace@example.com", "role": "member"},
    )
    assert updated.status_code == 200
    assert "Grace Updated" in updated.text

    deleted = hedron_client.post(
        "/users/2/delete",
        headers={**_auth(), "X-CSRF-Token": token, **hx},
        data={},
    )
    assert deleted.status_code == 200
    assert "Grace Updated" not in deleted.text


def test_plain_fastapi_mode(plain_client: TestClient) -> None:
    response = plain_client.get("/", headers=_auth())
    assert response.status_code == 200
    assert "Team Admin" in response.text
    assert "htmx.min.js" in response.text
    asset = plain_client.get("/hedron-static/htmx.min.js")
    assert asset.status_code == 200
    table = plain_client.get("/users/table", headers=_auth())
    assert "Grace Hopper" in table.text


def test_explorer_preview_available(hedron_client: TestClient) -> None:
    response = hedron_client.get("/hedron-explorer/", headers=_auth())
    assert response.status_code == 200
    assert "Hedron Explorer" in response.text


def test_private_cache_on_authenticated_dashboard(hedron_client: TestClient) -> None:
    response = hedron_client.get("/", headers=_auth())
    assert response.headers.get("Cache-Control") == "private, no-store"


def test_employee_save_requires_csrf(hedron_client: TestClient) -> None:
    denied = hedron_client.post(
        "/employees/save",
        headers={**_auth(), "Content-Type": "application/json"},
        json={
            "updates": [{"row_key": "e1", "field": "name", "value": "Ada2", "row_version": "1"}],
            "inserts": [],
            "deletes": [],
            "dataset_version": "1",
        },
    )
    assert denied.status_code == 403

    seeded = hedron_client.get("/", headers=_auth())
    token = seeded.cookies.get("hedron_csrf")
    assert token
    version = _MOD.EMPLOYEE_SOURCE.dataset_version
    ok = hedron_client.post(
        "/employees/save",
        headers={
            **_auth(),
            "Content-Type": "application/json",
            "X-CSRF-Token": token,
        },
        json={
            "updates": [
                {
                    "row_key": "e1",
                    "field": "name",
                    "value": "Ada2",
                    "row_version": version,
                }
            ],
            "inserts": [],
            "deletes": [],
            "dataset_version": version,
        },
    )
    assert ok.status_code == 200
    body = ok.json()
    assert body["ok"] is True


def test_employee_save_rejects_forged_readonly(hedron_client: TestClient) -> None:
    seeded = hedron_client.get("/", headers=_auth())
    token = seeded.cookies.get("hedron_csrf")
    assert token
    forged = hedron_client.post(
        "/employees/save",
        headers={
            **_auth(),
            "Content-Type": "application/json",
            "X-CSRF-Token": token,
        },
        json={
            "updates": [{"row_key": "e1", "field": "id", "value": "hack", "row_version": "1"}],
            "inserts": [],
            "deletes": [],
            "dataset_version": "1",
        },
    )
    assert forged.status_code == 200
    body = forged.json()
    assert body["ok"] is False
    assert body["errors"]


def test_color_mode_sets_cookie_and_theme(hedron_client: TestClient) -> None:
    seeded = hedron_client.get("/", headers=_auth())
    token = seeded.cookies.get("hedron_csrf")
    assert token
    response = hedron_client.post(
        "/color-mode",
        headers=_auth(),
        data={"color_mode": "dark", "csrf_token": token},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.cookies.get("hedron_color_mode") == "dark"
    themed = hedron_client.get("/", headers=_auth())
    assert 'data-theme="dark"' in themed.text


def test_roster_download_requires_auth(hedron_client: TestClient) -> None:
    assert hedron_client.get("/downloads/roster.csv").status_code == 401
    ok = hedron_client.get("/downloads/roster.csv", headers=_auth())
    assert ok.status_code == 200
    assert "text/csv" in ok.headers.get("content-type", "")
    assert "Ada" in ok.text or "name" in ok.text


def test_explorer_phase05_panels(hedron_client: TestClient) -> None:
    for path in ("/hedron-explorer/cache", "/hedron-explorer/data", "/hedron-explorer/auto"):
        response = hedron_client.get(path, headers=_auth())
        assert response.status_code == 200, path
    data = hedron_client.get("/hedron-explorer/data", headers=_auth())
    assert "Writable" in data.text or "writable" in data.text.lower() or "Data" in data.text


def test_plain_fastapi_phase05_routes(plain_client: TestClient) -> None:
    seeded = plain_client.get("/", headers=_auth())
    assert seeded.status_code == 200
    token = seeded.cookies.get("hedron_csrf")
    assert token
    save = plain_client.post(
        "/employees/save",
        headers={
            **_auth(),
            "Content-Type": "application/json",
            "X-CSRF-Token": token,
        },
        json={"updates": [], "inserts": [], "deletes": [], "dataset_version": "1"},
    )
    assert save.status_code == 200
    roster = plain_client.get("/downloads/roster.csv", headers=_auth())
    assert roster.status_code == 200
    summary = plain_client.get("/api/team-summary", headers=_auth())
    assert summary.status_code == 200
