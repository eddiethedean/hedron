#!/usr/bin/env python3
"""Shared helpers for phase 0.39 rich-surface / OptimisticMutation gates."""

from __future__ import annotations

import subprocess
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.39.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_39.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_RICH_ELEMENTS_039.md"
RICH_SURFACE = ROOT / "docs" / "implementation" / "RICH_SURFACE_039.md"
INTERACTION = ROOT / "docs" / "implementation" / "WEB_COMPONENT_INTERACTION_CONTRACTS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-039" / "BRIEF.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-039.md"
INVENTORY = ROOT / "docs" / "acceptance" / "rich-surface-inventory-039.toml"
FLEET_INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-039.toml"
AT_PROTOCOL = ROOT / "docs" / "acceptance" / "human-at" / "039" / "PROTOCOL.md"
AT_DISPOSITION = ROOT / "docs" / "acceptance" / "human-at" / "039" / "DISPOSITION.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"

EXPECTED_GATES = (
    "DATA-039",
    "OPTIMISTIC-039",
    "CHARTLINK-039",
    "RICH-039",
    "WORKER-039",
    "PERF-039",
    "A11Y-039",
    "REGRESS-039",
    "PKG-039",
)

TRACKING_ISSUE = "#94"
MEDIUM_ISSUES = (
    73,
    84,
    102,
    104,
    105,
    107,
    113,
    115,
    116,
    117,
    118,
    119,
    120,
    121,
    176,
    188,
    189,
    190,
    191,
    192,
    193,
    194,
    221,
    240,
    241,
    247,
    248,
)

# Populated as implementation evidence lands.
GATE_TESTS: dict[str, list[str]] = {
    "DATA-039": [
        "tests/unit/test_data_039_abi.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "OPTIMISTIC-039": [
        "tests/unit/test_data_039_abi.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "CHARTLINK-039": [
        "tests/unit/test_data_039_abi.py",
        "tests/unit/test_phase17_cross_filter.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "RICH-039": [
        "tests/unit/test_rich_worker_039.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "WORKER-039": [
        "tests/unit/test_rich_worker_039.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "PERF-039": [
        "tests/unit/test_perf_a11y_039.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "A11Y-039": [
        "tests/unit/test_perf_a11y_039.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "REGRESS-039": [
        "tests/unit/test_regress_039_issues.py",
        "tests/unit/test_data_editor_039_js.py",
        "tests/unit/test_phase039_packet.py",
    ],
    "PKG-039": ["tests/unit/test_phase039_packet.py"],
}

PACKET_FILES = (
    GATE,
    RELEASE_PACKET,
    IMPLEMENTATION,
    RICH_SURFACE,
    INTERACTION,
    RFC,
    REVIEW_BRIEF,
    UPGRADE,
    INVENTORY,
    FLEET_INVENTORY,
    AT_PROTOCOL,
    AT_DISPOSITION,
    DECISIONS,
)


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path}")


def gate_state(gate_id: str) -> str | None:
    if not GATE.is_file():
        return None
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for row in data.get("evidence") or []:
        if isinstance(row, dict) and str(row.get("id", "")).strip() == gate_id:
            return str(row.get("state", "")).strip()
    return None


def rfc_is_accepted() -> bool:
    return RFC.is_file() and "**Status:** Accepted" in RFC.read_text(encoding="utf-8")[:800]


def rfc_resolved_questions_present() -> bool:
    return RFC.is_file() and "## Resolved questions (D-067)" in RFC.read_text(encoding="utf-8")


def d067_present() -> bool:
    return DECISIONS.is_file() and "| D-067 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def medium_issue_refs() -> tuple[str, ...]:
    return tuple(f"#{n}" for n in MEDIUM_ISSUES)


def missing_refine_citations() -> list[str]:
    """Require tracking and medium-issue refs in the contract packet."""
    errors: list[str] = []
    required = (RELEASE_PACKET, DECISIONS, ROADMAP, RFC)
    refs = (TRACKING_ISSUE, *medium_issue_refs())
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [ref for ref in refs if ref not in text]
        if missing:
            errors.append(f"{path}: missing 0.39 issue refs {missing}")
    if RFC.is_file() and not rfc_resolved_questions_present():
        errors.append("RFC-0060 must include 'Resolved questions (D-067)'")
    if DECISIONS.is_file():
        decisions = DECISIONS.read_text(encoding="utf-8")
        if "v0.38.0" not in decisions.split("| D-067 |", 1)[-1][:2500]:
            errors.append("D-067 must baseline Published v0.38.0")
    return errors


def run_pytest(paths: list[str]) -> int:
    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not rfc_is_accepted():
        errors.append("RFC-0060 must be Accepted")
    if not d067_present():
        errors.append("D-067 must be Accepted in DECISIONS.md")
    if not rfc_resolved_questions_present():
        errors.append("RFC-0060 must include Resolved questions (D-067)")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.39.toml")
    elif state not in {"Planned", "Implemented", "Verified"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    tests = GATE_TESTS.get(gate_id, [])
    if state == "Verified" and not tests:
        errors.append(f"{gate_id} is Verified but has no executable evidence tests bound")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    if tests:
        code = run_pytest(tests)
        if code:
            return code
    print(f"ok: {gate_id}")
    return 0
