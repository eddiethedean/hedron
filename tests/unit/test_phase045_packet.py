from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from _gate_045 import (  # noqa: E402
    EXPECTED_GATES,
    GATE_TESTS,
    TRACKING_ISSUE,
    accepted_contract_present,
    contract_refine_present,
)


def test_phase045_manifest_commands_exist() -> None:
    path = ROOT / "docs" / "acceptance" / "release-gate-0.45.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data["evidence"]
    found = tuple(row["id"] for row in rows)
    assert found == EXPECTED_GATES
    assert set(GATE_TESTS) == set(EXPECTED_GATES)
    assert GATE_TESTS["PKG-045"] == ["tests/unit/test_phase045_packet.py"]
    for gate_id, tests in GATE_TESTS.items():
        assert tests, gate_id
        if gate_id == "PKG-045":
            continue
        assert "tests/unit/test_phase045_packet.py" not in tests, gate_id
    for row in rows:
        command_path = ROOT / row["command"].removeprefix("python ")
        assert command_path.is_file(), row["command"]
        assert row["state"] in {"Planned", "Implemented", "Verified"}


def test_phase045_tracking_and_contract() -> None:
    assert TRACKING_ISSUE == "#328"
    assert accepted_contract_present()
    assert contract_refine_present()
    packet = (ROOT / "docs" / "acceptance" / "RELEASE_0_45.md").read_text(encoding="utf-8")
    assert TRACKING_ISSUE in packet
    assert "0.45" in packet
