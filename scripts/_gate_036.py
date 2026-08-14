#!/usr/bin/env python3
"""Shared paths and helpers for phase 0.36 Stage 0 / gate stubs."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.36.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_36.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_ELEMENTS_036.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-036" / "BRIEF.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-036.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
PLATFORM_IMPL = ROOT / "docs" / "implementation" / "WEB_COMPONENT_PLATFORM.md"
ELEMENTS_PKG = ROOT / "packages" / "hedron-elements"

EXPECTED_GATES = (
    "ABI-036",
    "ELEMENTS-036",
    "LIFECYCLE-036",
    "SSR-036",
    "STATE-036",
    "SECURITY-036",
    "A11Y-036",
    "BROWSER-036",
    "PKG-036",
)


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path}")


def fail_errors(errors: list[str], gate: str) -> bool:
    if not errors:
        return False
    for err in errors:
        print(f"{gate}: {err}", flush=True)
    return True


def gate_state(gate_id: str) -> str | None:
    if not GATE.is_file():
        return None
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for row in data.get("evidence") or []:
        if isinstance(row, dict) and str(row.get("id", "")).strip() == gate_id:
            return str(row.get("state", "")).strip()
    return None


def rfc_is_accepted() -> bool:
    if not RFC.is_file():
        return False
    text = RFC.read_text(encoding="utf-8")
    return "**Status:** Accepted" in text[:500]


def d064_present() -> bool:
    if not DECISIONS.is_file():
        return False
    return "| D-064 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def elements_package_absent() -> bool:
    """Stage 0 forbids creating the package tree."""
    return not ELEMENTS_PKG.exists()


def planned_stub_ok(gate_id: str) -> int:
    """Exit 0 while the gate remains Planned; refuse premature Verified claims."""
    errors: list[str] = []
    require_files(
        [GATE, RELEASE_PACKET, IMPLEMENTATION, RFC, REVIEW_BRIEF, UPGRADE, PLATFORM_IMPL],
        errors,
    )
    if not rfc_is_accepted():
        errors.append("RFC-0060 must be Accepted")
    if not d064_present():
        errors.append("D-064 must be Accepted in DECISIONS.md")
    if not elements_package_absent():
        errors.append(
            "Stage 0 forbids packages/hedron-elements; remove it or advance past Stage 0"
        )
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.36.toml")
    elif state == "Verified":
        errors.append(
            f"{gate_id} is Verified but Stage 0 stub has no cut evidence yet"
        )
    elif state not in {"Planned", "Implemented"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    if fail_errors(errors, gate_id):
        return 1
    print(f"ok: {gate_id} (Stage 0 planned stub)")
    return 0
