"""Shared packet and executable-test checks for phase 0.62."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.62.toml"
PACKET_FILES = (
    ROOT / "docs" / "acceptance" / "navigation-policy-contract-062.toml",
    ROOT / "docs" / "acceptance" / "optimistic-risk-inventory-062.toml",
    ROOT / "docs" / "acceptance" / "failure-identity-contract-062.toml",
    ROOT / "docs" / "acceptance" / "interaction-capability-inventory-062.toml",
    ROOT / "docs" / "acceptance" / "interaction-diagnostics-062.toml",
    ROOT / "docs" / "acceptance" / "interaction-browser-disposition-062.toml",
    ROOT / "docs" / "acceptance" / "interaction-budgets-062.toml",
    ROOT / "docs" / "acceptance" / "interaction-security-a11y-062.toml",
    ROOT / "docs" / "acceptance" / "interaction-upgrade-fixtures-062.md",
)
REPORT = ROOT / "docs" / "acceptance" / "evidence-062" / "gate-results-062.json"
RELEASE_EVIDENCE_TEST = "tests/unit/test_phase062_navigation.py"
EXPECTED_GATES = (
    "CONTRACT-062", "NAV-062", "FALLBACK-062", "PREFETCH-062", "TRANSITION-062",
    "OPTIMISM-062", "CONFLICT-062", "FAILURE-062", "IDENTITY-062", "SECURITY-062",
    "A11Y-062", "BROWSER-062", "PERF-062", "DOCS-062", "UPGRADE-062", "PKG-062",
    "DASHBOARD-062",
)


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict[str, object]]:
    rows = _load(GATE).get("evidence")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def validate_packet(*, allow_planned: bool = False) -> list[str]:
    errors: list[str] = []
    for path in (GATE, *PACKET_FILES, REPORT):
        if not path.is_file():
            errors.append(f"missing 0.62 packet file: {path.relative_to(ROOT)}")
    if errors:
        return errors
    gate = _load(GATE)
    if gate.get("phase") != "0.62" or gate.get("target") != "v0.62.0":
        errors.append("release gate must target v0.62.0")
    if gate.get("planning_baseline") != "v0.61.0":
        errors.append("release gate planning baseline must be v0.61.0")
    ids = tuple(str(row.get("id", "")) for row in _rows())
    if ids != EXPECTED_GATES:
        errors.append(f"release gate IDs/order do not match 0.62 contract: {ids}")
    states = {str(row.get("id")): str(row.get("state")) for row in _rows()}
    if not allow_planned and any(state == "Planned" for state in states.values()):
        errors.append("implemented packet cannot contain Planned gates")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report_rows = report.get("gates", [])
    report_ids = tuple(row.get("id") for row in report_rows if isinstance(row, dict))
    if report_ids != EXPECTED_GATES:
        errors.append("0.62 evidence report IDs/order do not match the manifest")
    report_states = {str(row.get("id")): str(row.get("state")) for row in report_rows}
    if report_states != states:
        errors.append("0.62 evidence report states do not match the manifest")
    for path in PACKET_FILES:
        if path.suffix == ".toml" and _load(path).get("phase") != "0.62":
            errors.append(f"packet has wrong phase: {path.relative_to(ROOT)}")
    return errors


def _run_tests() -> int:
    python = ROOT / ".venv" / "bin" / "python"
    executable = str(python) if python.is_file() else sys.executable
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "")
    return subprocess.call(
        [executable, "-m", "pytest", "-q", "--tb=short", "-n", "0", RELEASE_EVIDENCE_TEST],
        cwd=ROOT,
        env=env,
    )


def check_gate(gate_id: str, *, verify: bool = False, allow_planned: bool = False) -> int:
    errors = validate_packet(allow_planned=allow_planned)
    if gate_id not in EXPECTED_GATES:
        errors.append(f"unknown gate {gate_id}")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    state = next(str(row.get("state")) for row in _rows() if row.get("id") == gate_id)
    if state == "Omitted":
        print(f"ok: {gate_id} (explicitly omitted from the 0.62 cut)")
        return 0
    if verify or os.environ.get("HEDRON_GATE_VERIFY") == "1":
        return _run_tests()
    print(f"ok: {gate_id} (implemented; executable evidence is available with --verify)")
    return 0
