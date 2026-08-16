"""Shared constants and contract helpers for the phase 0.43 gate."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.43.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "interaction-capability-inventory-043.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_43.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-043.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "INTERACTION_HANDLES_043.md"
API = ROOT / "docs" / "api" / "REFRESHABLE_VIEWS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0070-REFRESHABLE-VIEWS.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

PACKET_FILES = (GATE, INVENTORY, PACKET, UPGRADE, IMPLEMENTATION, API, RFC)
TRACKING_ISSUE = "#311"

EXPECTED_GATES = (
    "VIEW-043",
    "COMMAND-043",
    "UPDATE-043",
    "SECURITY-043",
    "A11Y-043",
    "BROWSER-043",
    "TOOLING-043",
    "COMPAT-043",
    "PERF-043",
    "DOCS-043",
    "REGRESS-043",
    "PKG-043",
)
EXPECTED_REQUIREMENT_RANGES = (
    "IH-VIEW-001..009",
    "IH-BIND-001..006",
    "IH-CMD-001..007",
    "IH-REFRESH-001..007",
    "IH-PATCH-001..008",
    "IH-HOST-001..007",
    "IH-HOST-002..006",
    "IH-SEC-001..007",
    "IH-DX-001..007",
    "IH-EXT-001..007",
    "IH-QUAL-001..004",
    "IH-QUAL-005..007",
    "IH-QUAL-008",
    "IH-QUAL-009",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-071 | Accepted |" in decisions


def cross_phase_refinement_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-073 | Accepted |" in decisions and all(
        marker in combined
        for marker in (
            "FragmentHandle[Bind, Content]",
            "ActionHandle[Input, Result]",
            "structural binding",
            "dynamic/observed",
        )
    )


GATE_TESTS: dict[str, list[str]] = {
    "VIEW-043": ["tests/unit/test_views_043.py"],
    "COMMAND-043": ["tests/unit/test_commands_043.py"],
    "UPDATE-043": ["tests/unit/test_updates_043.py"],
    "SECURITY-043": ["tests/security/test_security_043.py"],
    "A11Y-043": ["tests/a11y/test_a11y_043.py"],
    "BROWSER-043": ["tests/browser/test_browser_043.py"],
    "TOOLING-043": ["tests/unit/test_tooling_043.py"],
    "COMPAT-043": ["tests/unit/test_compat_043.py"],
    "PERF-043": ["tests/performance/test_perf_043.py"],
    "DOCS-043": ["tests/unit/test_docs_043.py"],
    "REGRESS-043": ["tests/unit/test_regress_043.py"],
    "PKG-043": ["tests/unit/test_phase043_packet.py"],
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


def run_pytest(paths: list[str]) -> int:
    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0070 and D-071 must remain Accepted")
    if not cross_phase_refinement_present():
        errors.append("D-073 and the frozen 0.43/0.44 boundary must remain present")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.43.toml")
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

