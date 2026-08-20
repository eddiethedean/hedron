"""COMPAT-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    CONTRACT_VERSION,
    CURRENT_CONTRACT_VERSION,
    PREVIOUS_CONTRACT_VERSION,
    check_contract_version,
    check_fixture_version,
    compatibility_policy_dict,
    negotiate_protocol,
    protocol_matrix,
)


def test_compat_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["COMPAT-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_current_previous_matrix() -> None:
    assert CURRENT_CONTRACT_VERSION == CONTRACT_VERSION == "hedron-portable-1"
    assert PREVIOUS_CONTRACT_VERSION == "hedron-portable-1"
    matrix = protocol_matrix()
    assert matrix["current"] == matrix["previous"] == "hedron-portable-1"
    assert negotiate_protocol(CURRENT_CONTRACT_VERSION).ok
    assert negotiate_protocol(PREVIOUS_CONTRACT_VERSION).ok
    assert not negotiate_protocol("hedron-portable-2").ok


def test_policy_exposes_negotiation() -> None:
    policy = compatibility_policy_dict()
    assert "hedron-portable-1" in policy["negotiable_contract_versions"]
    assert check_contract_version("hedron-portable-1").ok
    assert check_fixture_version("1.0.0").ok
    assert not check_fixture_version("9.0.0").ok
