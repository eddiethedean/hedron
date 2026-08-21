"""CONTRACT-056 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core.security_plane import (
    CONFORMANCE_PROFILE_VERSION,
    EVENT_CODES,
    SecurityPolicy,
    SecurityProfile,
)


def test_contract_056_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.56.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["CONTRACT-056"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0083-SECURITY-CONTROL-PLANE.md").is_file()
    contract = tomllib.loads(
        Path("docs/acceptance/security-contract-056.toml").read_text(encoding="utf-8")
    )
    assert contract["composition_object"] == "SecurityPolicy"
    assert contract["shared_schema_import"] == "hedron_core.security_plane"


def test_security_policy_composition_presets() -> None:
    development = SecurityPolicy.from_name("development")
    standard = SecurityPolicy.from_name("standard")
    strict = SecurityPolicy.from_name("strict")
    assert development.profile is SecurityProfile.DEVELOPMENT
    assert standard.conformance_profile_version == CONFORMANCE_PROFILE_VERSION
    assert standard.request_budget_limits is not None
    assert strict.intent_required is True
    assert strict.posture_strict is True
    assert set(EVENT_CODES) >= {
        "ctx.rejected",
        "sens.denied",
        "sink.denied",
        "egress.denied",
        "intent.rejected",
        "budget.exceeded",
    }
