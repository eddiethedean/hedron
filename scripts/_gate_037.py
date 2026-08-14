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

# Open high-severity issues owned by phase 0.37 (D-065 amendment).
# Issue bodies remain normative for REGRESS-037; cut requires them closed.
HIGH_SEVERITY_ISSUES = (230, 231, 232, 233, 234, 235, 236, 237)
ROADMAP = ROOT / "docs" / "ROADMAP.md"

# Populated in Stage 1+ as evidence lands.
GATE_TESTS: dict[str, list[str]] = {
    "FORM-037": [
        "tests/unit/test_elements_037_form.py",
        "tests/integration/test_elements_037_hosts.py",
    ],
    "VALIDITY-037": [
        "tests/unit/test_elements_037_validity.py",
        "tests/security/test_elements_037_security.py",
    ],
    "PRIMITIVE-037": [
        "tests/unit/test_elements_037_primitives.py",
        "tests/browser/test_elements_037_primitives.py",
    ],
    "ACTIONSTATE-037": [
        "tests/unit/test_elements_037_actionstate.py",
        "tests/browser/test_elements_037_actionstate.py",
    ],
    "INTERACT-037": [
        "tests/browser/test_elements_037_interact.py",
        "tests/unit/test_elements_037_gesture_catalog.py",
    ],
    "HTMX-037": [
        "tests/browser/test_elements_037_htmx.py",
        "tests/integration/test_elements_037_htmx_hosts.py",
    ],
    "AT-037": ["tests/a11y/test_elements_037_a11y.py"],
    "REGRESS-037": [
        "tests/unit/test_elements_037_regress.py",
        "tests/unit/test_phase037_packet.py",
    ],
}


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


def high_severity_issue_refs() -> tuple[str, ...]:
    return tuple(f"#{n}" for n in HIGH_SEVERITY_ISSUES)


def missing_high_severity_citations() -> list[str]:
    """Require every 0.37 high-severity issue to be named in the packet."""
    errors: list[str] = []
    required = (
        RELEASE_PACKET,
        DECISIONS,
        ROADMAP,
        GATE,
    )
    refs = high_severity_issue_refs()
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [ref for ref in refs if ref not in text]
        if missing:
            errors.append(f"{path}: missing high-severity issue refs {missing}")
    if DECISIONS.is_file():
        decisions = DECISIONS.read_text(encoding="utf-8")
        if "Amendment to D-065 (high-severity remediations)" not in decisions:
            errors.append("DECISIONS.md: missing D-065 high-severity amendment")
    return errors


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
