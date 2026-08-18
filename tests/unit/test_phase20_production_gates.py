"""Phase 0.20 PROD-020 production security gates."""

from __future__ import annotations

import pytest

from hedron_core.production_gate import (
    RISK_ACCEPTANCE_ENV,
    RISK_DEVELOPMENT_PROFILE,
    RISK_WEAK_SECRET,
    assert_production_security_config,
    parsed_risk_acceptance,
)


def test_production_rejects_weak_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="weak-session-secret"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret="replace-in-production",
            explorer_mode="off",
            content_security_policy="default-src 'self'",
        )


@pytest.mark.parametrize("secret", ["x", "password", "dev", "short-but-not-placeholder"])
def test_production_rejects_short_session_secrets(
    monkeypatch: pytest.MonkeyPatch, secret: str
) -> None:
    """#196: gate message promises short secrets are refused."""
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="weak-session-secret"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret=secret,
            explorer_mode="off",
            content_security_policy="default-src 'self'",
        )


def test_production_accepts_long_non_placeholder_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    assert_production_security_config(
        production=True,
        security_profile="standard",
        session_secret="a-sufficiently-long-production-secret",
        explorer_mode="off",
        content_security_policy="default-src 'self'",
    )


def test_production_rejects_development_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="security-development"):
        assert_production_security_config(
            production=True,
            security_profile="development",
            session_secret="a-sufficiently-long-production-secret",
            explorer_mode="off",
            content_security_policy="default-src 'self'",
        )


def test_risk_acceptance_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.setenv(
        RISK_ACCEPTANCE_ENV,
        f"{RISK_WEAK_SECRET},{RISK_DEVELOPMENT_PROFILE},missing-csp",
    )
    assert_production_security_config(
        production=True,
        security_profile="development",
        session_secret="dev",
        explorer_mode="off",
        content_security_policy=None,
    )


def test_parsed_risk_acceptance_normalizes() -> None:
    assert "weak-session-secret" in parsed_risk_acceptance(" Weak-Session-Secret , other ")


def test_production_rejects_explorer_development(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="explorer-development"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret="a-sufficiently-long-production-secret",
            explorer_mode="development",
            content_security_policy="default-src 'self'",
        )


def test_production_rejects_external_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="external-redirects"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret="a-sufficiently-long-production-secret",
            explorer_mode="off",
            allow_external_redirects=True,
            content_security_policy="default-src 'self'",
        )


def test_production_rejects_missing_csp_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="missing-csp"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret="a-sufficiently-long-production-secret",
            explorer_mode="off",
            content_security_policy=None,
        )


def test_hedron_constructor_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    from hedron import Hedron

    with pytest.raises(RuntimeError, match="Production security gate|weak-session-secret"):
        Hedron(
            title="demo",
            security="standard",
            explorer="off",
            session_secret="replace-in-production",
            production=True,
        )


def test_production_rejects_missing_session_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    """#260: None must fail the gate, not skip the weak-secret check."""
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="weak-session-secret"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret=None,
            explorer_mode="off",
            content_security_policy="default-src 'self'",
        )


def test_production_skips_secret_when_sessions_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    assert_production_security_config(
        production=True,
        security_profile="standard",
        session_secret=None,
        sessions_enabled=False,
        explorer_mode="off",
        content_security_policy="default-src 'self'",
    )


def test_hedron_refuses_none_session_secret_when_sessions_enabled() -> None:
    """#260: never install SessionMiddleware(secret_key=None)."""
    from hedron import Hedron

    with pytest.raises(ValueError, match="session_secret"):
        Hedron(
            title="x",
            security="standard",
            explorer="off",
            session_secret=None,
            production=False,
        )


def test_hedron_allows_none_secret_when_sessions_disabled() -> None:
    from starlette.middleware.sessions import SessionMiddleware

    from hedron import Hedron

    app = Hedron(
        title="x",
        security="standard",
        explorer="off",
        session_secret=None,
        enable_sessions=False,
        production=False,
    )
    assert not any(m.cls is SessionMiddleware for m in app.user_middleware)


def test_hedron_production_rejects_none_session_secret(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    from hedron import Hedron

    with pytest.raises(RuntimeError, match="weak-session-secret"):
        Hedron(
            title="demo",
            security="standard",
            explorer="off",
            session_secret=None,
            production=True,
        )


def test_401_flask_production_rejects_development_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    monkeypatch.setattr(
        "hedron_core.production_gate.assert_durable_backends",
        lambda **_kwargs: None,
    )
    from flask import Flask

    from hedron_core.security_policy import SecurityPolicy
    from hedron_flask.blueprint import attach_hedron_to_flask

    app = Flask(__name__)
    app.secret_key = "a-sufficiently-long-production-secret"

    class _Ext:
        auth_signal = None
        security_policy = SecurityPolicy.from_name("development")
        csrf_cookie_name = "hedron_csrf"

    with pytest.raises(RuntimeError, match="security-development"):
        attach_hedron_to_flask(app, _Ext(), auto_csrf_cookie=False, security="development")
