"""EXPLORER-026: secured-mode authz, audit, CSP, payload, production refusal."""

from __future__ import annotations

import warnings

import pytest
from fastapi import Depends, HTTPException, status
from starlette.testclient import TestClient

from hedron import Hedron
from hedron_explorer import router as explorer_router_mod


def _deny() -> None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="auth required")


def _allow() -> None:
    return None


def test_secured_anonymous_denied() -> None:
    app = Hedron(
        title="ex026",
        security="standard",
        explorer="secured",
        session_secret="test-secret-ex026",
    )
    client = TestClient(app)
    assert client.get("/hedron-explorer/").status_code == 401


def test_secured_with_auth_dependency_allows() -> None:
    app = Hedron(
        title="ex026",
        security="standard",
        explorer="secured",
        session_secret="test-secret-ex026",
        explorer_dependencies=[Depends(_allow)],
    )
    client = TestClient(app)
    response = client.get("/hedron-explorer/")
    assert response.status_code == 200
    assert "Hedron Explorer" in response.text


def test_secured_authz_dependency_can_refuse() -> None:
    app = Hedron(
        title="ex026",
        security="standard",
        explorer="secured",
        session_secret="test-secret-ex026",
        explorer_dependencies=[Depends(_deny)],
    )
    client = TestClient(app)
    assert client.get("/hedron-explorer/").status_code == 401


def test_production_refuses_development_explorer(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        app = Hedron(
            title="ex026",
            security="standard",
            explorer="development",
            session_secret="test-secret-ex026-prod",
            production=True,
        )
    assert app.hedron_explorer_mode == "off"
    assert any("development mode is disabled in production" in str(w.message) for w in caught)
    client = TestClient(app)
    assert client.get("/hedron-explorer/").status_code == 404


def test_explorer_off_absent_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    app = Hedron(
        title="ex026",
        security="standard",
        explorer="off",
        session_secret="test-secret-ex026-prod",
        production=True,
    )
    client = TestClient(app)
    assert client.get("/hedron-explorer/").status_code == 404


def test_audit_log_records_events() -> None:
    explorer_router_mod._AUDIT.clear()
    explorer_router_mod._audit("ex026_probe", detail="unit")
    assert explorer_router_mod._AUDIT
    event = explorer_router_mod._AUDIT[0]
    assert event["event"] == "ex026_probe"
    assert "ts" in event


def test_rate_limit_structures_exist() -> None:
    # Bounded in-memory structures — payload/rate-limit posture for EXPLORER-026.
    assert explorer_router_mod._TRACE.maxlen == 100
    assert explorer_router_mod._AUDIT.maxlen == 200


def test_csp_compatible_html_shell() -> None:
    app = Hedron(
        title="ex026",
        security="standard",
        explorer="secured",
        session_secret="test-secret-ex026",
        explorer_dependencies=[Depends(_allow)],
    )
    client = TestClient(app)
    response = client.get("/hedron-explorer/")
    assert response.status_code == 200
    # No inline script javascript: handlers required for the shell to load.
    assert "javascript:" not in response.text.lower()
