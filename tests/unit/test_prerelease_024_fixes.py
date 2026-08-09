"""Pre-release 0.24 security / host-parity regressions."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from flask import Flask

from hedron import Hedron, InteractionResult, OobUpdate, Text
from hedron_core.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionPolicy,
    authorize_htmx_target,
    authorize_oob_update,
)
from hedron_core.jobs import InMemoryJobBackend, job_authorized, job_authorized_http
from hedron_core.security_policy import SecurityPolicy, SecurityProfile
from hedron.security.csrf import _csrf_cookie_should_be_secure
from hedron_flask.csrf import csrf_cookie_should_be_secure
from hedron_flask.responses import interaction_response as flask_interaction_response


def test_oob_without_regions_rejects_arbitrary_element_id() -> None:
    with pytest.raises(ValueError, match="declared fragment regions"):
        authorize_oob_update(OobUpdate(content=Text("x"), element_id="admin-secret"), regions=())


def test_oob_without_regions_allows_reserved_toast() -> None:
    authorize_oob_update(OobUpdate(content=Text("ok"), element_id="hedron-toast"), regions=())


def test_htmx_missing_target_with_declared_regions_fails_closed() -> None:
    policy = InteractionPolicy(declared_regions=(FragmentRegion(id="main", selector="#main"),))
    with pytest.raises(FragmentRegionError, match="require HX-Target"):
        authorize_htmx_target(policy, None, is_htmx=True)


def test_job_tenant_only_does_not_authorize_arbitrary_subject() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, tenant_id="ten")
    status = backend.get(handle.job_id)
    assert status is not None
    assert job_authorized(status, auth_subject=None, tenant_id="ten")
    assert not job_authorized(status, auth_subject="eve", tenant_id="ten")
    assert not job_authorized_http(status, auth_subject="eve", tenant_id="ten")
    # Tenant-only HTTP poll must not invent a subject; matching None+tenant is allowed.
    assert job_authorized_http(status, auth_subject=None, tenant_id="ten")
    assert not job_authorized_http(status, auth_subject=None, tenant_id=None)


def test_job_http_requires_exact_scope_match() -> None:
    backend = InMemoryJobBackend()
    handle = backend.submit("t", {}, auth_subject="alice", tenant_id="t1")
    status = backend.get(handle.job_id)
    assert status is not None
    assert job_authorized_http(status, auth_subject="alice", tenant_id="t1")
    assert not job_authorized_http(status, auth_subject="alice", tenant_id=None)
    assert not job_authorized_http(status, auth_subject="bob", tenant_id="t1")


def test_interaction_result_status_code_rejects_bool() -> None:
    with pytest.raises(TypeError, match="status_code"):
        InteractionResult(content=None, status_code=True)  # type: ignore[arg-type]


def test_interaction_result_status_code_coerces_str() -> None:
    result = InteractionResult(content=None, status_code="204")  # type: ignore[arg-type]
    assert result.status_code == 204
    assert type(result.status_code) is int


def test_fastapi_csrf_secure_under_hedron_env_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    policy = SecurityPolicy.from_name("standard")
    assert _csrf_cookie_should_be_secure(None, policy) is True
    monkeypatch.delenv("HEDRON_ENV", raising=False)


def test_flask_csrf_secure_under_hedron_env_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv("FLASK_ENV", raising=False)
    monkeypatch.delenv("ENV", raising=False)
    app = Flask(__name__)
    with app.test_request_context("/", environ_base={"wsgi.url_scheme": "http"}):
        from flask import request

        assert csrf_cookie_should_be_secure(request) is True
    monkeypatch.delenv("HEDRON_ENV", raising=False)


def test_flask_204_rejects_oob() -> None:
    app = Flask(__name__)
    regions = (FragmentRegion(id="main", selector="#main"),)
    with app.test_request_context(
        "/",
        headers={"HX-Request": "true", "HX-Target": "#main"},
    ):
        response = flask_interaction_response(
            InteractionResult(
                content=None,
                status_code=204,
                oob=(OobUpdate(content=Text("toast"), element_id="hedron-toast"),),
            ),
            fragment_regions=regions,
        )
    assert response.status_code == 403


def test_fastapi_oob_arbitrary_id_without_regions_403() -> None:
    app = Hedron(title="t", security="standard", session_secret="test-secret", explorer="off")

    @app.component("/oob")
    def oob() -> InteractionResult:
        return InteractionResult(
            content=Text("primary"),
            oob=(OobUpdate(content=Text("leak"), element_id="admin-secret"),),
            policy=InteractionPolicy(allow_undeclared_targets=True),
        )

    client = TestClient(app)
    response = client.get(
        "/oob",
        headers={"HX-Request": "true", "HX-Target": "#anything"},
    )
    assert response.status_code == 403
