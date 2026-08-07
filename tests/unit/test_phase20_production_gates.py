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
