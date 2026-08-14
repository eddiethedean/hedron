#!/usr/bin/env python3
"""Shared helpers for phase 0.38 high-fidelity chart gates."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.38.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_38.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_CHARTS_038.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0069-HIGH-FIDELITY-CHARTS.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-038" / "BRIEF.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-038.md"
INVENTORY = ROOT / "docs" / "acceptance" / "chart-capability-inventory-038.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
CHARTS_PKG = ROOT / "packages" / "hedron-charts"

EXPECTED_GATES = (
    "GRAMMAR-038",
    "RENDER-038",
    "DESIGN-038",
    "VISUAL-038",
    "INTERACT-038",
    "A11Y-038",
    "PERF-038",
    "EXPORT-038",
    "SECURITY-038",
    "COMPAT-038",
    "DOCS-038",
    "REGRESS-038",
    "PKG-038",
)

# Populated as implementation evidence lands.
GATE_TESTS: dict[str, list[str]] = {}


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
    return RFC.is_file() and "**Status:** Accepted" in RFC.read_text(encoding="utf-8")[:500]


def d066_present() -> bool:
    return DECISIONS.is_file() and "| D-066 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def run_pytest(paths: list[str]) -> int:
    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(
        [GATE, RELEASE_PACKET, IMPLEMENTATION, RFC, REVIEW_BRIEF, UPGRADE, INVENTORY, DECISIONS],
        errors,
    )
    if not rfc_is_accepted():
        errors.append("RFC-0069 must be Accepted")
    if not d066_present():
        errors.append("D-066 must be Accepted in DECISIONS.md")
    if not (CHARTS_PKG / "pyproject.toml").is_file():
        errors.append("packages/hedron-charts is required")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.38.toml")
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
