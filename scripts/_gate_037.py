#!/usr/bin/env python3
"""Shared helpers for phase 0.37 release gates."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.37.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_37.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_ELEMENTS_037.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-037" / "BRIEF.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-037.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
PLATFORM_IMPL = ROOT / "docs" / "implementation" / "WEB_COMPONENT_PLATFORM.md"
INTERACTION = ROOT / "docs" / "implementation" / "WEB_COMPONENT_INTERACTION_CONTRACTS.md"
ELEMENTS_PKG = ROOT / "packages" / "hedron-elements"
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-037.toml"

EXPECTED_GATES = (
    "FORM-037",
    "VALIDITY-037",
    "PRIMITIVE-037",
    "ACTIONSTATE-037",
    "INTERACT-037",
    "HTMX-037",
    "AT-037",
    "REGRESS-037",
    "PKG-037",
)

# Populated in Stage 1+ as evidence lands.
GATE_TESTS: dict[str, list[str]] = {}


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
    return "**Status:** Accepted" in RFC.read_text(encoding="utf-8")[:500]


def d064_present() -> bool:
    if not DECISIONS.is_file():
        return False
    return "| D-064 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def d065_present() -> bool:
    if not DECISIONS.is_file():
        return False
    return "| D-065 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def elements_package_present() -> bool:
    return (ELEMENTS_PKG / "pyproject.toml").is_file()


def run_pytest(paths: list[str], gate: str) -> int:
    cmd = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *cmd, flush=True)
    return subprocess.call(cmd, cwd=ROOT)


def check_gate(gate_id: str, *, require_package: bool = True) -> int:
    errors: list[str] = []
    require_files(
        [
            GATE,
            RELEASE_PACKET,
            IMPLEMENTATION,
            RFC,
            REVIEW_BRIEF,
            UPGRADE,
            PLATFORM_IMPL,
            INTERACTION,
        ],
        errors,
    )
    if not rfc_is_accepted():
        errors.append("RFC-0060 must be Accepted")
    if not d064_present():
        errors.append("D-064 must be Accepted in DECISIONS.md")
    if not d065_present():
        errors.append("D-065 must be Accepted in DECISIONS.md")
    if require_package and not elements_package_present():
        errors.append("packages/hedron-elements is required")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.37.toml")
    elif state not in {"Planned", "Implemented", "Verified"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    if fail_errors(errors, gate_id):
        return 1
    tests = GATE_TESTS.get(gate_id, [])
    if tests:
        code = run_pytest(tests, gate_id)
        if code != 0:
            return code
    print(f"ok: {gate_id}")
    return 0
