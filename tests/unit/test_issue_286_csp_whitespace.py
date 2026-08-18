"""#286: whitespace-only Content-Security-Policy must fail the production gate."""

from __future__ import annotations

import pytest

from hedron_core.production_gate import RISK_ACCEPTANCE_ENV, assert_production_security_config


def test_whitespace_only_csp_is_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEDRON_ENV", "production")
    monkeypatch.delenv(RISK_ACCEPTANCE_ENV, raising=False)
    with pytest.raises(RuntimeError, match="missing-csp"):
        assert_production_security_config(
            production=True,
            security_profile="standard",
            session_secret="a-sufficiently-long-production-secret",
            explorer_mode="off",
            content_security_policy="   ",
        )
