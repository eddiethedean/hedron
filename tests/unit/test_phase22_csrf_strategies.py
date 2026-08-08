"""Phase 0.22 CSRF strategy gates (CSRF-022)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from starlette.requests import Request

from hedron import Hedron, Page, Text
from hedron.security.csrf import csrf_token_for_request, validate_csrf
from hedron.security.policy import SecurityPolicy
from hedron_core.csrf_strategy import (
    CsrfValidationError,
    DoubleSubmitCookieCsrf,
    SessionTokenCsrf,
)


def test_default_profile_resolves_double_submit_strategy() -> None:
    policy = SecurityPolicy.from_name("standard")
    strategy = policy.resolve_csrf_strategy()
    assert isinstance(strategy, DoubleSubmitCookieCsrf)
    assert strategy.cookie_name == "hedron_csrf"
    assert strategy.form_field == "csrf_token"


def test_csrf_disabled_resolves_none() -> None:
    policy = SecurityPolicy(csrf_enabled=False)
    assert policy.resolve_csrf_strategy() is None


def test_session_token_csrf_validates_without_starlette_session() -> None:
    expected = "session-token-abc"

    def get_expected(_request: object) -> str | None:
        return expected

    strategy = SessionTokenCsrf(get_expected=get_expected)
    strategy.validate(object(), form_value=expected, header_value=None)
    strategy.validate(object(), form_value=None, header_value=expected)
    try:
        strategy.validate(object(), form_value="wrong", header_value=None)
        raise AssertionError("expected CsrfValidationError")
    except CsrfValidationError:
        pass


def test_fastapi_session_token_strategy_accepts_header() -> None:
    expected = "db-backed-token"

    def get_expected(_request: object) -> str | None:
        return expected

    policy = SecurityPolicy(
        csrf_enabled=True,
        csrf=SessionTokenCsrf(get_expected=get_expected),
    )
    app = Hedron(title="csrf-022", security=policy, explorer="off", session_secret="test")

    @app.page("/")
    def home(request: Request) -> Page:
        token = csrf_token_for_request(request, policy)
        return Page(Text(token), title="home")

    @app.action("/save")
    def save() -> Page:
        return Page(Text("ok"), title="saved")

    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert expected in response.text

    denied = client.post("/save")
    assert denied.status_code == 403

    ok = client.post("/save", headers={"X-CSRF-Token": expected})
    assert ok.status_code == 200
    assert "ok" in ok.text


def test_validate_csrf_skips_when_disabled() -> None:
    policy = SecurityPolicy(csrf_enabled=False)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/",
        "headers": [],
        "query_string": b"",
    }
    request = Request(scope)
    validate_csrf(request, policy)  # does not raise


def test_session_token_issue_missing_does_not_500_get() -> None:
    policy = SecurityPolicy(
        csrf_enabled=True,
        csrf=SessionTokenCsrf(get_expected=lambda _r: None),
    )
    app = Hedron(title="csrf-issue", security=policy, explorer="off", session_secret="test")

    @app.page("/")
    def home() -> Page:
        return Page(Text("ok"), title="home")

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "ok" in response.text


def test_session_token_prefers_form_over_header() -> None:
    strategy = SessionTokenCsrf(get_expected=lambda _r: "expected")
    strategy.validate(object(), form_value="expected", header_value="wrong")
    try:
        strategy.validate(object(), form_value="wrong", header_value="expected")
        raise AssertionError("expected CsrfValidationError")
    except CsrfValidationError:
        pass


def test_security_policy_equality_includes_csrf_strategy() -> None:
    a = SecurityPolicy(csrf=SessionTokenCsrf(get_expected=lambda _r: "a"))
    b = SecurityPolicy(csrf=SessionTokenCsrf(get_expected=lambda _r: "b"))
    assert a != b
    assert len({a, b}) == 2
