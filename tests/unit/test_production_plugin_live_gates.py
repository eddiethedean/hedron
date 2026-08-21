"""Production plugin deny-default and experimental-live gates (1.0 readiness)."""

from __future__ import annotations

import pytest

from hedron_core.production_gate import (
    RISK_ACCEPTANCE_ENV,
    RISK_EXPERIMENTAL_LIVE,
    RISK_PLUGINS_DISCOVER_ALL,
    assert_experimental_live_allowed,
    resolve_production_plugins,
)


def test_resolve_plugins_non_production_keeps_discover_all(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    assert resolve_production_plugins(None, production=False) is None
    assert resolve_production_plugins(["hedron_data"], production=False) == ["hedron_data"]


def test_resolve_plugins_production_denies_omitted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.warns(UserWarning, match="deny-by-default"):
        assert resolve_production_plugins(None, production=True) == []


def test_resolve_plugins_production_allowlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    assert resolve_production_plugins(["hedron_data"], production=True) == ["hedron_data"]
    assert resolve_production_plugins([], production=True) == []


def test_resolve_plugins_production_discover_all_risk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.setenv(RISK_ACCEPTANCE_ENV, RISK_PLUGINS_DISCOVER_ALL)
    with pytest.warns(UserWarning, match="discover-all"):
        assert resolve_production_plugins(None, production=True) is None


def test_experimental_live_refused_in_production(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="experimental-live"):
        assert_experimental_live_allowed(production=True)


def test_experimental_live_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.setenv(RISK_ACCEPTANCE_ENV, RISK_EXPERIMENTAL_LIVE)
    assert_experimental_live_allowed(production=True)
