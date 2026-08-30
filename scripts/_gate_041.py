#!/usr/bin/env python3
"""Shared executable evidence for phase 0.41 gates."""

from __future__ import annotations

import subprocess
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs/acceptance/release-gate-0.41.toml"
EXPECTED = (
    "COMPOSE-041",
    "STATE-041",
    "NAV-041",
    "TRACE-041",
    "FALLBACK-041",
    "BROWSER-041",
    "REGRESS-041",
    "PKG-041",
)
PACKET = (
    ROOT / "docs/acceptance/RELEASE_0_41.md",
    ROOT / "docs/implementation/HEDRON_COMPOSITION_041.md",
    ROOT / "docs/acceptance/upgrade-fixtures-041.md",
    ROOT / "docs/acceptance/security-review-041/BRIEF.md",
    ROOT / "docs/acceptance/security-review-041/REDACTED_REPORT.md",
    ROOT / "docs/acceptance/security-review-041/DISPOSITION.toml",
)


def check(gate_id: str) -> int:
    rows = tomllib.loads(GATE.read_text())["evidence"]
    ids = tuple(row["id"] for row in rows)
    errors = []
    if ids != EXPECTED:
        errors.append(f"unexpected gates: {ids}")
    if gate_id not in ids:
        errors.append(f"missing gate {gate_id}")
    errors.extend(f"missing {path}" for path in PACKET if not path.is_file())
    for marker, path in (
        ("D-069", ROOT / "docs/DECISIONS.md"),
        ("Resolved questions (D-069)", ROOT / "docs/rfcs/RFC-0060-WEB-COMPONENT-PLATFORM.md"),
    ):
        if marker not in path.read_text():
            errors.append(f"{path}: missing {marker}")
    if errors:
        print("\n".join(errors))
        return 1
    tests = ["tests/unit/test_phase041_contracts.py", "tests/unit/test_phase041_packet.py"]
    if gate_id in {
        "COMPOSE-041",
        "STATE-041",
        "NAV-041",
        "TRACE-041",
        "FALLBACK-041",
        "BROWSER-041",
    }:
        tests.append("tests/unit/test_phase041_browser_module.py")
    if gate_id == "BROWSER-041":
        tests.append("tests/browser/test_phase041_browser.py")
    if gate_id == "REGRESS-041":
        tests.extend(("tests/unit/test_regress_041_issues.py", "tests/conformance/test_job_sse.py"))
    return subprocess.call(["uv", "run", "pytest", "-q", "--tb=short", *tests], cwd=ROOT)
