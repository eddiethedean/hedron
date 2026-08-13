"""Regression tests for #195 — whitespace-padded production env values."""

from __future__ import annotations

import pytest

from hedron_core.compile_gate import is_production_env
from hedron_core.csrf_secure import csrf_cookie_should_be_secure
from hedron_core.production_gate import assert_production_security_config


@pytest.mark.parametrize(
    "value",
    [
        "production",
        "production ",
        " production",
        "\tproduction\n",
        "PROD",
        "prod ",
        "\tprod\n",
        "Production",
    ],
)
def test_is_production_env_strips_whitespace(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("HEDRON_ENV", value)
    assert is_production_env() is True


@pytest.mark.parametrize("value", ["", "development", "staging", "prodution"])
def test_is_production_env_non_production(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    if value:
        monkeypatch.setenv("HEDRON_ENV", value)
    else:
        monkeypatch.delenv("HEDRON_ENV", raising=False)
    assert is_production_env() is False


def test_production_security_gate_honors_padded_hedron_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production ")
    with pytest.raises(RuntimeError, match="Production security gate failed"):
        assert_production_security_config(
            production=None,
            security_profile="development",
            session_secret="hedron-dev-secret-change-me",
            explorer_mode="development",
            content_security_policy=None,
        )


def test_csrf_extra_env_vars_strip_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HEDRON_ENV", raising=False)
    monkeypatch.setenv("FLASK_ENV", "production ")
    assert (
        csrf_cookie_should_be_secure(
            force_secure=None,
            request_is_secure=False,
            extra_production_env_vars=("FLASK_ENV", "ENV"),
        )
        is True
    )
