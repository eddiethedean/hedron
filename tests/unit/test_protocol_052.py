"""PROTOCOL-052 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_conformance import (
    CONTRACT_VERSION,
    PROTOCOL_CURRENT,
    PROTOCOL_PREVIOUS,
    check_contract_version,
    negotiate_protocol,
    protocol_matrix,
)


def test_protocol_052_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.52.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["PROTOCOL-052"]["state"] in {"Planned", "Implemented", "Verified"}
    assert Path("docs/rfcs/RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md").is_file()


def test_protocol_seed_unchanged() -> None:
    assert CONTRACT_VERSION == "hedron-portable-1"
    assert PROTOCOL_CURRENT == CONTRACT_VERSION
    assert PROTOCOL_PREVIOUS == CONTRACT_VERSION


def test_negotiate_accepts_current_and_refuses_unknown() -> None:
    ok = negotiate_protocol("hedron-portable-1")
    assert ok.ok
    assert ok.code == "CONF-COMPAT-NEGOTIATE-OK"
    refused = negotiate_protocol("hedron-portable-99")
    assert not refused.ok
    assert "NEGOTIATE-REFUSED" in refused.code or "COMPAT" in refused.code
    assert not check_contract_version("hedron-future-1").ok


def test_protocol_matrix_fail_closed() -> None:
    matrix = protocol_matrix()
    assert matrix["current"] == "hedron-portable-1"
    assert matrix["previous"] == "hedron-portable-1"
    assert matrix["replace_seed_without_negotiation"] is False
    assert matrix["forward_unknown"] == "fail-closed"
