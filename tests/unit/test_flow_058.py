"""FLOW-058 evidence + progressive facade HTTP regressions."""

from __future__ import annotations

import re

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from hedron import (
    AuthDenied,
    AuthSuccess,
    DashboardWorkspace,
    DesignSystem,
    Hedron,
    RateLimitPolicy,
    SessionAuthFlow,
    Text,
    UploadFlow,
)
from hedron.upload import UploadBudget, UploadField, read_upload_capped
from hedron_core.bundles import FeatureBundle
from hedron_core.diagnostics import HedronError


def test_session_auth_flow_to_bundle() -> None:
    class Creds(BaseModel):
        username: str = Field(min_length=1, max_length=80)
        password: str = Field(min_length=1, max_length=80)

    flow = SessionAuthFlow(
        credentials=Creds,
        authenticate=lambda creds: (
            AuthSuccess(principal=creds.username) if creds.password == "x" else AuthDenied()
        ),
        serialize_principal=lambda principal: principal,
        load_principal=lambda stored: stored,
        login_path="/login",
        logout_path="/logout",
        after_login="/",
        rate_limit=RateLimitPolicy(limit=10, window_seconds=60.0),
        rotation="on_login",
    )
    bundle = flow.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert bundle.logical_id


def test_upload_flow_to_bundle() -> None:
    def allow() -> None:
        return None

    flow = UploadFlow(
        name="docs",
        field=UploadField(name="file", budget=UploadBudget(maximum_size=1_000_000)),
        authorize=Depends(allow),
        store=lambda handle: handle.accept(),
        result=lambda stored: Text(str(stored)),
    )
    bundle = flow.to_bundle()
    assert isinstance(bundle, FeatureBundle)
    assert bundle.logical_id


def test_upload_flow_custom_field_name_http_round_trip() -> None:
    """#591: FileUpload name must match FastAPI File alias."""

    def allow() -> None:
        return None

    app = Hedron(title="upload", security="development", explorer="off", session_secret="x" * 32)
    flow = UploadFlow(
        name="docs",
        field=UploadField(
            name="document",
            budget=UploadBudget(maximum_size=10_000, maximum_count=3),
        ),
        authorize=Depends(allow),
        store=lambda handle: "stored-id",
        result=lambda stored: Text(str(stored)),
    )
    app.include_feature(flow)
    client = TestClient(app)
    page = client.get("/docs/upload")
    assert page.status_code == 200
    assert 'name="document"' in page.text
    assert re.search(r"\bmultiple\b", page.text)
    csrf = client.cookies.get("hedron_csrf")
    assert csrf
    missing = client.post(
        "/docs/upload",
        data={"csrf_token": csrf},
        files={"file": ("a.txt", b"hello", "text/plain")},
    )
    assert missing.status_code == 422
    ok = client.post(
        "/docs/upload",
        data={"csrf_token": csrf},
        files={"document": ("a.txt", b"hello", "text/plain")},
    )
    assert ok.status_code == 200
    assert "stored-id" in ok.text


def test_upload_flow_rejects_missing_authorize() -> None:
    with pytest.raises(HedronError):
        UploadFlow(
            name="docs",
            field=UploadField(name="file", budget=UploadBudget(maximum_size=100)),
            authorize=None,  # type: ignore[arg-type]
            store=lambda handle: handle.accept(),
            result=lambda stored: Text(str(stored)),
        )


@pytest.mark.anyio
async def test_read_upload_capped_rejects_before_full_buffer() -> None:
    class _Stream:
        def __init__(self) -> None:
            self._chunks = [b"a" * 60, b"b" * 60]

        async def read(self, size: int = -1) -> bytes:
            del size
            if not self._chunks:
                return b""
            return self._chunks.pop(0)

    with pytest.raises(ValueError, match="maximum size"):
        await read_upload_capped(_Stream(), maximum_size=100)


def test_session_auth_include_and_login_round_trip() -> None:
    class Creds(BaseModel):
        username: str = Field(min_length=1, max_length=80)
        password: str = Field(min_length=1, max_length=80)

    app = Hedron(title="auth", security="standard", explorer="off", session_secret="test-secret")

    @app.screen("/", title="Home")
    def home() -> object:
        return Text("home")

    flow = SessionAuthFlow(
        credentials=Creds,
        authenticate=lambda creds: (
            AuthSuccess(principal=creds.username) if creds.password == "secret" else AuthDenied()
        ),
        serialize_principal=lambda principal: principal,
        load_principal=lambda stored: stored,
        login_path="/login",
        logout_path="/logout",
        after_login="/",
        rate_limit=RateLimitPolicy(limit=20, window_seconds=60.0),
        rotation="on_login",
    )
    app.include_feature(flow)
    assert flow.login_form is not None
    assert callable(flow.current_principal())

    client = TestClient(app)
    page = client.get("/login")
    assert page.status_code == 200
    assert 'name="username"' in page.text
    assert 'name="password"' in page.text or 'type="password"' in page.text
    assert "hedron_login_csrf" in page.text
    assert "csrf_token" in page.text

    login_csrf = re.search(r'name="hedron_login_csrf"[^>]*value="([^"]+)"', page.text)
    csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.text)
    assert login_csrf and csrf

    denied = client.post(
        "/login",
        data={
            "username": "ada",
            "password": "secret",
            "csrf_token": csrf.group(1),
            # missing / wrong login csrf
            "hedron_login_csrf": "forged",
        },
    )
    assert denied.status_code == 403

    page2 = client.get("/login")
    login_csrf = re.search(r'name="hedron_login_csrf"[^>]*value="([^"]+)"', page2.text)
    csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page2.text)
    assert login_csrf and csrf
    ok = client.post(
        "/login",
        data={
            "username": "ada",
            "password": "secret",
            "csrf_token": csrf.group(1),
            "hedron_login_csrf": login_csrf.group(1),
        },
        follow_redirects=False,
    )
    assert ok.status_code in {303, 302}
    assert ok.headers.get("location") == "/"


def test_dashboard_filter_form_and_urlencoded_redirect() -> None:
    class Filters(BaseModel):
        region: str = "west"

    def load(filters: Filters) -> dict[str, str]:
        return {"region": filters.region}

    app = Hedron(title="dash", security="standard", explorer="off", session_secret="test-secret")
    workspace = DashboardWorkspace(
        name="sales",
        path="/sales",
        title="Sales",
        filters=Filters,
        load=load,
        panels={"summary": lambda data: Text(data["region"])},
        history="replace",
    )
    app.include_feature(workspace)
    client = TestClient(app)
    page = client.get("/sales")
    assert page.status_code == 200
    assert "/sales/filters" in page.text or "filters" in page.text
    assert 'name="region"' in page.text
    assert "csrf_token" in page.text

    csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.text)
    assert csrf
    response = client.post(
        "/sales/filters",
        data={"region": "a&b=1", "csrf_token": csrf.group(1)},
        follow_redirects=False,
    )
    assert response.status_code in {303, 302}
    location = response.headers.get("location") or ""
    assert location.startswith("/sales?")
    assert "a%26b%3D1" in location or "a%26b=1" in location
    assert response.headers.get("HX-Replace-Url") == location


def test_design_system_persisted_on_hedron() -> None:
    design = DesignSystem.brand("acme", accent="#b45309")
    app = Hedron(
        title="styled",
        security="development",
        explorer="off",
        theme=design,
        session_secret="test-secret",
    )
    assert app.hedron_design_system is design
    assert app.state.hedron_design_system is design
    assert app.hedron_theme == "acme"
