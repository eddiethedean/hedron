"""Shared packet and executable-test checks for phase 0.61."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.61.toml"
PACKET_FILES = (
    ROOT / "docs" / "acceptance" / "action-state-contract-061.toml",
    ROOT / "docs" / "acceptance" / "async-region-contract-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-capability-inventory-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-diagnostics-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-host-disposition-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-trace-schema-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-budgets-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-security-a11y-061.toml",
    ROOT / "docs" / "acceptance" / "interaction-upgrade-fixtures-061.md",
    ROOT / "docs" / "acceptance" / "phase061-surface-contract.toml",
)
REPORT = ROOT / "docs" / "acceptance" / "evidence-061" / "gate-results-061.json"
RELEASE_EVIDENCE_TEST = "tests/unit/test_phase061_action_state.py"
EXPECTED_GATES = (
    "CONTRACT-061",
    "ACTIONSTATE-061",
    "OPERATION-061",
    "ASYNC-061",
    "SURFACE-061",
    "VISUAL-061",
    "CONCURRENCY-061",
    "STALE-061",
    "FORM-061",
    "JOB-061",
    "HOST-061",
    "TRACE-061",
    "SECURITY-061",
    "A11Y-061",
    "PERF-061",
    "DOCS-061",
    "UPGRADE-061",
    "PKG-061",
)


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict[str, object]]:
    rows = _load(GATE).get("evidence")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def validate_packet(*, allow_planned: bool) -> list[str]:
    errors: list[str] = []
    for path in (GATE, *PACKET_FILES, REPORT):
        if not path.is_file():
            errors.append(f"missing 0.61 packet file: {path.relative_to(ROOT)}")
    if errors:
        return errors
    gate = _load(GATE)
    if gate.get("phase") != "0.61" or gate.get("target") != "v0.61.0":
        errors.append("release gate must target v0.61.0")
    if gate.get("planning_baseline") != "v0.60.2":
        errors.append("release gate planning baseline must be v0.60.2")
    ids = tuple(str(row.get("id", "")) for row in _rows())
    if ids != EXPECTED_GATES:
        errors.append(f"release gate IDs/order do not match 0.61 contract: {ids}")
    states = {str(row.get("id")): str(row.get("state")) for row in _rows()}
    if allow_planned:
        unexpected = [gate_id for gate_id, state in states.items() if state != "Planned"]
        if unexpected:
            errors.append(f"stage-0 packet must keep gates Planned: {unexpected}")
    else:
        non_verified = [gate_id for gate_id, state in states.items() if state != "Verified"]
        if non_verified:
            errors.append(f"0.61 release has non-Verified gates: {non_verified}")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    if report.get("summary", {}).get("total") != len(EXPECTED_GATES):
        errors.append("0.61 evidence report total must be 18")
    report_rows = report.get("gates", [])
    report_ids = tuple(row.get("id") for row in report_rows if isinstance(row, dict))
    if report_ids != EXPECTED_GATES:
        errors.append("0.61 evidence report IDs/order do not match the manifest")
    report_states = {str(row.get("id")): str(row.get("state")) for row in report_rows}
    if report_states != states:
        errors.append("0.61 evidence report states do not match the manifest")
    for path in PACKET_FILES:
        if path.suffix == ".toml" and _load(path).get("phase") != "0.61":
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


def check_gate(gate_id: str, *, allow_planned: bool = False) -> int:
    errors = validate_packet(allow_planned=allow_planned)
    if gate_id not in EXPECTED_GATES:
        errors.append(f"unknown gate {gate_id}")
    if not (ROOT / RELEASE_EVIDENCE_TEST).is_file():
        errors.append(f"missing release evidence corpus: {RELEASE_EVIDENCE_TEST}")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    state = next(str(row.get("state")) for row in _rows() if row.get("id") == gate_id)
    if state == "Verified" or os.environ.get("HEDRON_GATE_VERIFY") == "1":
        return _run_tests()
    print(f"ok: {gate_id} ({state}; executable evidence is not yet claimed)")
    return 0
