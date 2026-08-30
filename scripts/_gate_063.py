"""Shared packet and executable-test checks for phase 0.63."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.63.toml"
REPORT = ROOT / "docs" / "acceptance" / "evidence-063" / "gate-results-063.json"
RELEASE_EVIDENCE_TEST = "tests/unit/test_phase063_release_evidence.py"
EXPECTED_GATES = (
    "CONTRACT-063",
    "THEME-063",
    "PALETTE-063",
    "PARTS-063",
    "EXPORT-063",
    "BUNDLE-063",
    "INSPECT-063",
    "THEME-CHECK-063",
    "MATRIX-063",
    "VISUAL-063",
    "TRACE-063",
    "PROFILER-063",
    "PROFILE-SAFE-063",
    "CHECK-063",
    "CHECK-SAFE-063",
    "SOURCE-063",
    "METADATA-063",
    "IDENTITY-063",
    "MIGRATE-063",
    "INTEROP-063",
    "SECURITY-063",
    "A11Y-063",
    "PERF-063",
    "CONFORMANCE-063",
    "DOCS-063",
    "UPGRADE-063",
    "PKG-063",
)
PROGRESSIVE = frozenset()
PACKET_FILES = (
    "interaction-capability-inventory-063.toml",
    "theme-resolution-contract-063.toml",
    "theme-export-contract-063.toml",
    "component-parts-manifest-063.json",
    "theme-conformance-contract-063.toml",
    "component-state-matrix-063.toml",
    "visualization-theme-contract-063.toml",
    "interaction-trace-conformance-063.toml",
    "interaction-profiler-contract-063.toml",
    "interaction-check-catalog-063.toml",
    "element-metadata-abi-063.toml",
    "react-migration-disposition-063.toml",
    "interaction-diagnostics-063.toml",
    "interaction-budgets-063.toml",
    "interaction-upgrade-fixtures-063.md",
    "evidence-063/theme-contract.json",
    "evidence-063/component-manifest.json",
    "evidence-063/element-metadata.json",
    "evidence-063/package-identity.json",
    "evidence-063/state-matrix.json",
    "evidence-063/interaction-profile.json",
    "evidence-063/react-migration.json",
    "evidence-063/interaction-checks.json",
    "evidence-063/runtime-baseline.json",
)


def _load(path: Path) -> dict[str, object]:
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _rows() -> list[dict[str, object]]:
    rows = _load(GATE).get("evidence")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def validate_packet(*, allow_planned: bool = False) -> list[str]:
    errors: list[str] = []
    paths = [GATE, REPORT, *(GATE.parent / name for name in PACKET_FILES)]
    errors.extend(
        f"missing 0.63 packet file: {path.relative_to(ROOT)}"
        for path in paths
        if not path.is_file()
    )
    if errors:
        return errors
    gate = _load(GATE)
    if gate.get("phase") != "0.63" or gate.get("target") != "v0.63.0":
        errors.append("release gate must target v0.63.0")
    if gate.get("planning_baseline") != "v0.62.0":
        errors.append("release gate planning baseline must be v0.62.0")
    ids = tuple(str(row.get("id", "")) for row in _rows())
    if ids != EXPECTED_GATES:
        errors.append(f"release gate IDs/order do not match 0.63 contract: {ids}")
    states = {str(row.get("id")): str(row.get("state")) for row in _rows()}
    if not allow_planned and any(state == "Planned" for state in states.values()):
        errors.append("implemented packet cannot contain Planned gates")
    if set(states) != set(EXPECTED_GATES):
        errors.append("release gate states do not cover the exact gate set")
    if any(state != "Verified" for state in states.values()):
        errors.append("all phase 0.63 gates must be Verified")
    report = _load(REPORT)
    report_rows = report.get("gates", [])
    report_ids = tuple(row.get("id") for row in report_rows if isinstance(row, dict))
    if report_ids != EXPECTED_GATES:
        errors.append("0.63 evidence report IDs/order do not match the manifest")
    report_states = {str(row.get("id")): str(row.get("state")) for row in report_rows}
    if report_states != states:
        errors.append("0.63 evidence report states do not match the manifest")
    summary = report.get("summary") or {}
    if summary.get("total") != len(EXPECTED_GATES):
        errors.append("0.63 evidence report total is incorrect")
    if summary.get("planned") != 0 or summary.get("verified") != len(EXPECTED_GATES):
        errors.append("0.63 evidence report summary does not match gate states")
    return errors


def _run_tests() -> int:
    python = ROOT / ".venv" / "bin" / "python"
    executable = str(python) if python.is_file() else sys.executable
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "")
    return subprocess.call(
        [
            executable,
            "-m",
            "pytest",
            "-q",
            "--tb=short",
            "-n",
            "0",
            RELEASE_EVIDENCE_TEST,
            "tests/unit/test_phase063_theme_contract.py",
            "tests/unit/test_phase063_trace_contract.py",
            "tests/unit/test_phase063_tooling.py",
        ],
        cwd=ROOT,
        env=env,
    )


def check_gate(gate_id: str, *, verify: bool = False, allow_planned: bool = False) -> int:
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
    if verify or os.environ.get("HEDRON_GATE_VERIFY") == "1":
        return _run_tests()
    print(f"ok: {gate_id} ({state}; executable evidence is available with --verify)")
    return 0
