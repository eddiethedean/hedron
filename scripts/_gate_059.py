"""Shared evidence checks for phase 0.59.

The release packet intentionally keeps gate state separate from executable
checks: a Planned gate can validate its packet and fixture wiring without
being misreported as browser-verified.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "acceptance" / "modern-css-contract-059.toml"
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.59.toml"
TRACKING = ROOT / "docs" / "acceptance" / "modern-css-tracking-059.toml"
EVIDENCE = ROOT / "docs" / "acceptance" / "evidence-059"
RELEASE_EVIDENCE_TEST = "tests/unit/test_phase059_release_evidence.py"

EXPECTED_GATES = (
    "CONTRACT-059",
    "COMPILER-059",
    "CASCADE-059",
    "TOKENS-059",
    "COLOR-059",
    "CONTAINER-059",
    "LAYOUT-059",
    "TYPE-059",
    "CONTROL-059",
    "CHROME-059",
    "WORKFLOW-059",
    "OVERLAY-059",
    "MOTION-059",
    "MEDIA-059",
    "A11Y-059",
    "DX-059",
    "VISUAL-059",
    "PERF-059",
    "SECURITY-059",
    "COMPAT-059",
    "CONSUMER-059",
    "REGRESS-059",
    "PKG-059",
)

GATE_TESTS: dict[str, tuple[str, ...]] = {
    "CONTRACT-059": ("tests/unit/test_phase059_foundation.py",),
    "COMPILER-059": ("tests/unit/test_css.py", "tests/unit/test_phase059_contract_matrix.py"),
    "CASCADE-059": (
        "tests/unit/test_theme_assets_build.py",
        "tests/unit/test_phase059_contract_matrix.py",
    ),
    "TOKENS-059": ("tests/unit/test_scope_058.py", "tests/unit/test_phase059_contract_matrix.py"),
    "COLOR-059": (
        "tests/unit/test_scope_058.py",
        "tests/unit/test_brand_058.py",
        "tests/unit/test_phase059_contract_matrix.py",
    ),
    "CONTAINER-059": (
        "tests/unit/test_phase059_foundation.py",
        "tests/unit/test_layout_055.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "LAYOUT-059": (
        "tests/unit/test_layout_055.py",
        "tests/unit/test_layout_057.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "TYPE-059": (
        "tests/unit/test_theme_assets_build.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "CONTROL-059": (
        "tests/unit/test_phase059_foundation.py",
        "tests/unit/test_phase15_controls.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "CHROME-059": (
        "tests/unit/test_phase15_controls.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "WORKFLOW-059": (
        "tests/unit/test_workflow_057.py",
        "tests/unit/test_workflow_053.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "OVERLAY-059": (
        "tests/unit/test_phase059_foundation.py",
        "tests/unit/test_dialog.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "MOTION-059": (
        "tests/unit/test_charts_038_visual.py",
        "tests/unit/test_theme_assets_build.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "MEDIA-059": (
        "tests/unit/test_charts_038_visual.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "A11Y-059": (
        "tests/unit/test_phase18_presentation.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "DX-059": ("tests/unit/test_docs_cli_snippets.py",),
    "VISUAL-059": (
        "tests/unit/test_visual_058.py",
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/browser/test_phase059_browser.py",
    ),
    "PERF-059": ("tests/unit/test_theme_assets_build.py",),
    "SECURITY-059": (
        "tests/unit/test_security_058.py",
        "tests/unit/test_css.py",
        "tests/unit/test_phase059_contract_matrix.py",
    ),
    "COMPAT-059": (
        "tests/unit/test_css.py",
        "tests/unit/test_regress_058.py",
        "tests/unit/test_phase059_contract_matrix.py",
    ),
    "CONSUMER-059": ("tests/unit/test_pkg_058.py",),
    "REGRESS-059": ("tests/unit/test_regress_058.py",),
    "PKG-059": ("tests/unit/test_pkg_058.py",),
}


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _gate_state(gate_id: str) -> str | None:
    for row in _load(GATE).get("evidence", []):
        if isinstance(row, dict) and row.get("id") == gate_id:
            return str(row.get("state", ""))
    return None


def _validate_packet(gate_id: str) -> list[str]:
    errors: list[str] = []
    if not CONTRACT.is_file() or not GATE.is_file():
        return ["phase 0.59 contract or release gate is missing"]
    contract = _load(CONTRACT)
    gate = _load(GATE)
    tracking = _load(TRACKING)
    if contract.get("phase") != "0.59" or contract.get("decision") != "D-107":
        errors.append("contract must remain phase 0.59 under accepted D-107")
    compiler = contract.get("compiler")
    if not isinstance(compiler, dict) or compiler.get("manifest_format") != 2:
        errors.append("compiler manifest format must be 2")
    if not isinstance(compiler, dict) or compiler.get("accepted_manifest_readers") != [1, 2]:
        errors.append("v1 and v2 manifest readers must remain accepted")
    if not isinstance(compiler, dict) or compiler.get("runtime_compile") is not False:
        errors.append("runtime CSS compilation must remain disabled")
    if gate.get("target") != "v0.59.0" or gate.get("required_predecessor") != "v0.58.1":
        errors.append("release target or predecessor lock changed")
    report_name = gate.get("evidence_report")
    report_path = EVIDENCE / str(report_name) if isinstance(report_name, str) else None
    if report_path is None or not report_path.is_file():
        errors.append("23-gate execution report is missing")
    else:
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"23-gate execution report is unreadable: {exc}")
        else:
            summary = report.get("summary", {})
            rows = report.get("gates", [])
            if summary.get("total") != len(EXPECTED_GATES) or len(rows) != len(EXPECTED_GATES):
                errors.append("23-gate execution report must contain exactly 23 gates")
            report_ids = tuple(row.get("id") for row in rows if isinstance(row, dict))
            if report_ids != EXPECTED_GATES:
                errors.append("23-gate execution report IDs/order do not match the contract")
            manifest_states = {
                row.get("id"): row.get("state")
                for row in gate.get("evidence", [])
                if isinstance(row, dict)
            }
            report_states = {
                row.get("id"): row.get("state") for row in rows if isinstance(row, dict)
            }
            if report_states != manifest_states:
                errors.append("23-gate execution report states do not match release-gate manifest")
    entry = tracking.get("stage_1_entry")
    required_entry_flags = (
        "accepted_contract_refine",
        "hedron_umbrella_issue_filed",
        "hedron_workstream_issue_mirrors_filed",
        "consumer_issue_backlinks_added",
        "browser_capability_probe_locked",
        "parser_implementation_probe_locked",
        "explicit_set_recipe_probe_locked",
        "live_issue_audit_refreshed",
    )
    if not isinstance(entry, dict) or any(
        entry.get(flag) is not True for flag in required_entry_flags
    ):
        errors.append("Stage 1 entry packet is not fully locked")
    required_artifacts = (
        "baseline-0581.json",
        "parser-recipe-059.json",
        "capability-chromium-059.json",
        "capability-firefox-059.json",
        "capability-webkit-059.json",
        "release-matrix-059.json",
    )
    for artifact in required_artifacts:
        if not (EVIDENCE / artifact).is_file():
            errors.append(f"missing Stage 1 evidence artifact: {artifact}")
    ids = tuple(row.get("id") for row in gate.get("evidence", []) if isinstance(row, dict))
    if ids != EXPECTED_GATES:
        errors.append("release gate IDs/order do not match the 0.59 contract")
    if gate_id not in EXPECTED_GATES:
        errors.append(f"unknown gate {gate_id}")
    return errors


def _run_tests(paths: tuple[str, ...]) -> int:
    python = ROOT / ".venv" / "bin" / "python"
    executable = str(python) if python.is_file() else sys.executable
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "")
    command = [executable, "-m", "pytest", "-q", "--tb=short", "-n", "0", *paths]
    print("+", " ".join(command), flush=True)
    return subprocess.call(command, cwd=ROOT, env=env)


def check_gate(gate_id: str) -> int:
    errors = _validate_packet(gate_id)
    state = _gate_state(gate_id)
    if state not in {"Planned", "Implemented", "Verified", "Deferred", "Excluded"}:
        errors.append(f"{gate_id} has invalid state {state!r}")
    for path in GATE_TESTS.get(gate_id, ()):
        if not (ROOT / path).is_file():
            errors.append(f"missing evidence test: {path}")
    if not (ROOT / RELEASE_EVIDENCE_TEST).is_file():
        errors.append(f"missing release evidence corpus: {RELEASE_EVIDENCE_TEST}")
    if errors:
        for error in errors:
            print(f"{gate_id}: {error}", flush=True)
        return 1
    if state == "Verified" or os.environ.get("HEDRON_GATE_VERIFY") == "1":
        paths = GATE_TESTS[gate_id]
        if RELEASE_EVIDENCE_TEST not in paths:
            paths = (*paths, RELEASE_EVIDENCE_TEST)
        return _run_tests(paths)
    print(f"ok: {gate_id} ({state}; executable evidence is not yet claimed)")
    return 0
