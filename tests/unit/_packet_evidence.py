"""Shared helpers for release-gate packet evidence tests (not product behavior)."""

from __future__ import annotations

import tomllib
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _pkg_gate_id(version: str) -> str:
    """Map ``0.43`` → ``PKG-043``."""
    major, minor, *_ = version.lstrip("v").split(".")
    return f"PKG-{major}{minor.zfill(2)}"


def _release_packet_name(version: str) -> str:
    """Map ``0.43`` → ``RELEASE_0_43.md``."""
    major, minor, *_ = version.lstrip("v").split(".")
    return f"RELEASE_{major}_{minor}.md"


def assert_phase_packet_manifest(
    *,
    version: str,
    expected_gates: Sequence[str],
    gate_tests: Mapping[str, Sequence[str]],
    packet_test_relpath: str,
) -> None:
    """Assert release-gate TOML rows, commands, and PKG self-reference inventory."""
    path = ROOT / "docs" / "acceptance" / f"release-gate-{version}.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data["evidence"]
    found = tuple(row["id"] for row in rows)
    assert found == tuple(expected_gates)
    assert set(gate_tests) == set(expected_gates)
    pkg_gate = _pkg_gate_id(version)
    assert gate_tests[pkg_gate] == [packet_test_relpath]
    for gate_id, tests in gate_tests.items():
        assert tests, gate_id
        if gate_id == pkg_gate:
            continue
        assert packet_test_relpath not in tests, gate_id
    for row in rows:
        command_path = ROOT / row["command"].removeprefix("python ")
        assert command_path.is_file(), row["command"]
        assert row["state"] in {"Planned", "Implemented", "Verified"}


def assert_phase_packet_tracking(
    *,
    version: str,
    tracking_issue: str,
    contract_checks: Sequence[Callable[[], bool]],
) -> None:
    """Assert release packet markdown cites the tracking issue and contracts."""
    for check in contract_checks:
        assert check()
    packet = (ROOT / "docs" / "acceptance" / _release_packet_name(version)).read_text(
        encoding="utf-8"
    )
    assert tracking_issue in packet
    assert version.lstrip("v") in packet
