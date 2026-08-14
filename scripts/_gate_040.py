#!/usr/bin/env python3
"""Shared helpers for phase 0.40 authoring / React migration gates."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.40.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_40.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_AUTHORING_040.md"
MATRIX = ROOT / "docs" / "implementation" / "REACT_MIGRATION_MATRIX_040.md"
INTERACTION = ROOT / "docs" / "implementation" / "WEB_COMPONENT_INTERACTION_CONTRACTS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-040" / "BRIEF.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-040.md"
INVENTORY = ROOT / "docs" / "acceptance" / "authoring-capability-inventory-040.toml"
FLEET_INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-040.toml"
AT_PROTOCOL = ROOT / "docs" / "acceptance" / "human-at" / "040" / "PROTOCOL.md"
AT_DISPOSITION = ROOT / "docs" / "acceptance" / "human-at" / "040" / "DISPOSITION.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"

EXPECTED_GATES = (
    "AUTHOR-040",
    "PLUGIN-040",
    "HDJ-040",
    "THEME-040",
    "EXPLORER-040",
    "CONF-040",
    "MIGRATE-040",
    "SUPPLY-040",
    "REGRESS-040",
    "PKG-040",
)

TRACKING_ISSUE = "#95"
MEDIUM_ISSUES = (162, 203, 204, 219, 220, 222)

PACKET_FILES = (
    RELEASE_PACKET,
    GATE,
    IMPLEMENTATION,
    MATRIX,
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

# Stage 0: bind only the packet unit test until Stage 1+ evidence lands.
GATE_TESTS: dict[str, list[str]] = {
    gate: ["tests/unit/test_phase040_packet.py"] for gate in EXPECTED_GATES
}


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path}")


def gate_state(gate_id: str) -> str | None:
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for row in data.get("evidence") or []:
        if row.get("id") == gate_id:
            return str(row.get("state", "")).strip()
    return None


def rfc_is_accepted() -> bool:
    return RFC.is_file() and "**Status:** Accepted" in RFC.read_text(encoding="utf-8")[:800]


def rfc_resolved_questions_present() -> bool:
    return RFC.is_file() and "Resolved questions (D-068)" in RFC.read_text(encoding="utf-8")


def d068_present() -> bool:
    return DECISIONS.is_file() and "| D-068 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def medium_issue_refs() -> tuple[str, ...]:
    return tuple(f"#{n}" for n in MEDIUM_ISSUES)


def missing_refine_citations() -> list[str]:
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
            errors.append(f"{path}: missing 0.40 issue refs {missing}")
    if RFC.is_file() and not rfc_resolved_questions_present():
        errors.append("RFC-0060 must include 'Resolved questions (D-068)'")
    if DECISIONS.is_file():
        decisions = DECISIONS.read_text(encoding="utf-8")
        if "v0.39.0" not in decisions.split("| D-068 |", 1)[-1][:2500]:
            errors.append("D-068 must baseline Published v0.39.0")
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
    if not d068_present():
        errors.append("D-068 must be Accepted in DECISIONS.md")
    if not rfc_resolved_questions_present():
        errors.append("RFC-0060 must include Resolved questions (D-068)")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.40.toml")
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
