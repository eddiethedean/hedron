"""Failure-path and async coverage for canonical auth and upload flows."""

from __future__ import annotations

import re
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from pydantic import BaseModel

from hedron import (
    AuthDenied,
    AuthSuccess,
    Hedron,
    RateLimitPolicy,
    SessionAuthFlow,
    Text,
    UploadFlow,
)
from hedron.security.login_csrf import LOGIN_CSRF_KEY
from hedron.upload import UploadBudget, UploadField
from hedron_core.diagnostics import HedronError


class Credentials(BaseModel):
    username: str
    password: str


def _auth_flow(**overrides: Any) -> SessionAuthFlow[Credentials, str, str]:
    values: dict[str, Any] = {
        "credentials": Credentials,
        "authenticate": lambda data: (
            AuthSuccess(principal=data.username) if data.password == "secret" else AuthDenied()
        ),
        "serialize_principal": lambda principal: principal,
        "load_principal": lambda stored: stored,
        "rate_limit": RateLimitPolicy(limit=10, window_seconds=60.0),
    }
    values.update(overrides)
    return SessionAuthFlow(**values)


def _app(title: str) -> Hedron:
    return Hedron(
        title=title,
        security="standard",
        explorer="off",
        session_secret=f"{title}-test-secret-32-bytes-long",
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"limit": 0},
        {"window_seconds": 0},
        {"window_seconds": -1},
        {"window_seconds": float("inf")},
        {"window_seconds": float("nan")},
        {"window_seconds": True},
    ],
)
def test_rate_limit_policy_rejects_invalid_bounds(kwargs: dict[str, object]) -> None:
    with pytest.raises(HedronError, match="Invalid rate limit"):
        RateLimitPolicy(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"after_login": "https://evil.test"}, "Unsafe after_login"),
        ({"rotation": "sometimes"}, "Invalid session rotation"),
    ],
)
def test_auth_flow_rejects_unsafe_configuration(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(HedronError, match=message):
        _auth_flow(**kwargs)


def test_current_principal_is_fail_closed_for_missing_or_invalid_session() -> None:
    flow = _auth_flow(load_principal=lambda stored: (_ for _ in ()).throw(ValueError(stored)))
    dependency = flow.current_principal()

    assert dependency(SimpleNamespace()) is None  # type: ignore[arg-type]
    assert dependency(SimpleNamespace(session=object())) is None  # type: ignore[arg-type]
    assert dependency(SimpleNamespace(session={})) is None  # type: ignore[arg-type]
    assert dependency(SimpleNamespace(session={flow.session_key: "bad"})) is None  # type: ignore[arg-type]


def test_session_rotation_preserves_login_csrf_and_rejects_immutable_sessions() -> None:
    flow = _auth_flow()
    session = {LOGIN_CSRF_KEY: "csrf", "old": "value"}
    flow._rotate_session(SimpleNamespace(session=session))
    assert session == {LOGIN_CSRF_KEY: "csrf"}

    with pytest.raises(HedronError, match="Session rotation unavailable"):
        flow._rotate_session(SimpleNamespace())
    with pytest.raises(HedronError, match="session.clear"):
        flow._rotate_session(SimpleNamespace(session=object()))

    never = _auth_flow(rotation="never")
    untouched = {"old": "value"}
    never._rotate_session(SimpleNamespace(session=untouched))
    assert untouched == {"old": "value"}


def test_authentication_denial_and_callback_exception_are_redacted() -> None:
    for flow in (
        _auth_flow(authenticate=lambda _data: AuthDenied()),
        _auth_flow(authenticate=lambda _data: (_ for _ in ()).throw(RuntimeError("secret"))),
    ):
        app = _app("auth-redaction")
        app.include(flow)
        client = TestClient(app)
        page = client.get("/login")
        login_csrf = re.search(r'name="hedron_login_csrf"[^>]*value="([^"]+)"', page.text)
        csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.text)
        assert login_csrf and csrf
        with pytest.raises(HedronError) as raised:
            client.post(
                "/login",
                data={
                    "username": "ada",
                    "password": "wrong",
                    "csrf_token": csrf.group(1),
                    "hedron_login_csrf": login_csrf.group(1),
                },
            )
        assert raised.value.diagnostic.code == "HED-AUTHFLOW-0002"
        assert "secret" not in str(raised.value)


def _allow() -> None:
    return None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"name": ""},
        {"name": "   "},
        {"field": object()},
        {"authorize": None},
        {"process": object()},
    ],
)
def test_upload_flow_rejects_invalid_configuration(kwargs: dict[str, object]) -> None:
    values: dict[str, object] = {
        "name": "docs",
        "field": UploadField(),
        "authorize": Depends(_allow),
        "store": lambda handle: handle.filename,
        "result": lambda stored: Text(str(stored)),
    }
    values.update(kwargs)
    with pytest.raises(HedronError):
        UploadFlow(**values)  # type: ignore[arg-type]


def test_upload_flow_async_callbacks_and_empty_result_surface() -> None:
    async def store(handle: object) -> str:
        return str(getattr(handle, "filename", "missing"))

    async def result(stored: object) -> object:
        return Text(f"stored:{stored}")

    app = _app("async-upload")
    flow = UploadFlow(
        name="async-docs",
        field=UploadField(budget=UploadBudget(maximum_size=100)),
        authorize=Depends(_allow),
        store=store,
        result=result,
    )
    app.include(flow)
    client = TestClient(app)

    assert "No upload result" in client.get("/async-docs/result").text
    csrf = client.get("/async-docs/upload").cookies.get("hedron_csrf")
    assert csrf
    response = client.post(
        "/async-docs/upload",
        data={"csrf_token": csrf},
        files={"file": ("report.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 200
    assert "stored:report.txt" in response.text
    assert "stored:report.txt" in client.get("/async-docs/result").text


def test_upload_store_failure_cleans_materialized_uploads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cleaned: list[object] = []

    def cleanup(handle: object) -> None:
        cleaned.append(handle)
        from hedron.upload import cleanup_upload as real_cleanup

        real_cleanup(handle)  # type: ignore[arg-type]

    monkeypatch.setattr("hedron.files.flow.cleanup_upload", cleanup)
    app = _app("upload-failure")
    app.include(
        UploadFlow(
            name="broken",
            field=UploadField(budget=UploadBudget(maximum_size=100)),
            authorize=Depends(_allow),
            store=lambda _handle: (_ for _ in ()).throw(RuntimeError("private path")),
            result=lambda stored: Text(str(stored)),
        )
    )
    client = TestClient(app)
    csrf = client.get("/broken/upload").cookies.get("hedron_csrf")
    assert csrf
    with pytest.raises(HedronError) as raised:
        client.post(
            "/broken/upload",
            data={"csrf_token": csrf},
            files={"file": ("report.txt", b"hello", "text/plain")},
        )
    assert "private path" not in str(raised.value)
    assert cleaned
    assert all(not getattr(handle, "owned", True) for handle in cleaned)


def test_upload_download_stub_is_authorized_and_fails_closed() -> None:
    app = _app("download-stub")
    flow = UploadFlow(
        name="downloads",
        field=UploadField(),
        authorize=Depends(_allow),
        authorize_download=Depends(_allow),
        store=lambda handle: handle.filename,
        result=lambda stored: Text(str(stored)),
    )
    app.include(flow)
    with pytest.raises(HedronError, match="Download not configured"):
        TestClient(app).get("/downloads/download")
