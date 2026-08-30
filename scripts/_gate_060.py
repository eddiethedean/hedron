"""Shared packet and executable-test checks for phase 0.60."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.60.toml"
CONTRACT = ROOT / "docs" / "acceptance" / "theme-platform-contract-060.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "theme-platform-inventory-060.toml"
TRACKING = ROOT / "docs" / "acceptance" / "theme-platform-tracking-060.toml"
COMPATIBILITY = ROOT / "docs" / "acceptance" / "theme-platform-compatibility-060.toml"
EVIDENCE = ROOT / "docs" / "acceptance" / "evidence-060"
REPORT = EVIDENCE / "gate-results-060.json"
RELEASE_EVIDENCE_TEST = "tests/unit/test_phase060_release_evidence.py"
PLANNING_BASELINE = "v0.59.0"
RELEASE_CANDIDATE = "0.60.0"

EXPECTED_GATES = (
    "CONTRACT-060",
    "RECONCILE-060",
    "COLOR-060",
    "PALETTE-060",
    "THEME-060",
    "VALIDATE-060",
    "PACKAGE-060",
    "A11Y-MODE-060",
    "RECIPE-060",
    "SCOPE-060",
    "PREFERENCE-060",
    "BRAND-060",
    "FEEDBACK-060",
    "WORKFLOW-060",
    "SCROLL-060",
    "CATALOG-060",
    "TOOLING-060",
    "EXPLORER-060",
    "CONFORMANCE-060",
    "DOCS-060",
    "VISUAL-060",
    "A11Y-060",
    "SECURITY-060",
    "PERF-060",
    "COMPAT-060",
    "REGRESS-060",
    "PKG-060",
)

GATE_TESTS = {
    "CONTRACT-060": ("tests/unit/test_phase060_release_evidence.py",),
    "RECONCILE-060": (
        "tests/unit/test_phase059_contract_matrix.py",
        "tests/unit/test_phase060_theme_platform.py",
    ),
    "COLOR-060": ("tests/unit/test_phase060_theme_platform.py", "tests/unit/test_brand_058.py"),
    "PALETTE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_brand_058.py",
        "tests/unit/test_theme_058.py",
    ),
    "THEME-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_theme_053.py",
        "tests/unit/test_theme_058.py",
    ),
    "VALIDATE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_recipe_058.py",
    ),
    "PACKAGE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_conformance_kit.py",
    ),
    "A11Y-MODE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_a11y_058.py",
    ),
    "RECIPE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_recipe_058.py",
    ),
    "SCOPE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_scope_058.py",
    ),
    "PREFERENCE-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/integration/test_theme_gallery.py",
    ),
    "BRAND-060": (
        "tests/unit/test_brand_058.py",
        "tests/browser/test_phase060_theme_platform.py",
    ),
    "FEEDBACK-060": ("tests/browser/test_phase060_theme_platform.py",),
    "WORKFLOW-060": (
        "tests/unit/test_workflow_057.py",
        "tests/browser/test_phase060_theme_platform.py",
    ),
    "SCROLL-060": ("tests/browser/test_phase060_theme_platform.py",),
    "CATALOG-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/integration/test_theme_gallery.py",
    ),
    "TOOLING-060": ("tests/unit/test_phase060_theme_platform.py",),
    "EXPLORER-060": (
        "tests/unit/test_explorer_040.py",
        "tests/integration/test_explorer_026.py",
    ),
    "CONFORMANCE-060": (
        "tests/unit/test_conformance_kit.py",
        "tests/unit/test_conform_056.py",
    ),
    "DOCS-060": ("tests/unit/test_phase060_release_evidence.py",),
    "VISUAL-060": (
        "tests/unit/test_visual_058.py",
        "tests/browser/test_phase060_theme_platform.py",
    ),
    "A11Y-060": (
        "tests/unit/test_a11y_058.py",
        "tests/browser/test_phase060_theme_platform.py",
    ),
    "SECURITY-060": (
        "tests/unit/test_security_058.py",
        "tests/unit/test_phase060_theme_platform.py",
    ),
    "PERF-060": ("tests/unit/test_theme_assets_build.py",),
    "COMPAT-060": (
        "tests/unit/test_phase059_release_evidence.py",
        "tests/unit/test_phase060_theme_platform.py",
    ),
    "REGRESS-060": ("tests/unit/test_phase059_release_evidence.py",),
    "PKG-060": (
        "tests/unit/test_phase060_theme_platform.py",
        "tests/unit/test_phase060_release_evidence.py",
    ),
}


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _gate_rows() -> list[dict[str, object]]:
    rows = _load(GATE).get("evidence")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def _state(gate_id: str) -> str | None:
    return next(
        (str(row.get("state", "")) for row in _gate_rows() if row.get("id") == gate_id),
        None,
    )


def validate_packet(*, allow_planned: bool) -> list[str]:
    errors: list[str] = []
    for path in (GATE, CONTRACT, INVENTORY, TRACKING, COMPATIBILITY, REPORT):
        if not path.is_file():
            errors.append(f"missing 0.60 packet file: {path.relative_to(ROOT)}")
    if errors:
        return errors
    gate = _load(GATE)
    contract = _load(CONTRACT)
    inventory = _load(INVENTORY)
    tracking = _load(TRACKING)
    if gate.get("phase") != "0.60" or gate.get("target") != "v0.60.0":
        errors.append("release gate must target v0.60.0")
    if gate.get("planning_baseline") != PLANNING_BASELINE:
        errors.append("release gate planning baseline must remain v0.59.0")
    if gate.get("required_predecessor") != "v0.59.0":
        errors.append("release gate predecessor must remain v0.59.0")
    if contract.get("phase") != "0.60" or inventory.get("phase") != "0.60":
        errors.append("contract and inventory must remain phase 0.60")
    if tracking.get("phase") != "0.60":
        errors.append("tracking packet must remain phase 0.60")
    ids = tuple(str(row.get("id", "")) for row in _gate_rows())
    if ids != EXPECTED_GATES:
        errors.append(f"release gate IDs/order do not match 0.60 contract: {ids}")
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    report_rows = report.get("gates", [])
    if report.get("summary", {}).get("total") != len(EXPECTED_GATES):
        errors.append("0.60 evidence report total must be 27")
    report_ids = tuple(row.get("id") for row in report_rows if isinstance(row, dict))
    if report_ids != EXPECTED_GATES:
        errors.append("0.60 evidence report IDs/order do not match the manifest")
    manifest_states = {row.get("id"): row.get("state") for row in _gate_rows()}
    report_states = {
        row.get("id"): row.get("state") for row in report_rows if isinstance(row, dict)
    }
    if manifest_states != report_states:
        errors.append("0.60 report states do not match the manifest")
    if allow_planned:
        unexpected = [gate_id for gate_id, state in manifest_states.items() if state != "Planned"]
        if unexpected:
            errors.append(f"stage-0 packet must keep gates Planned: {unexpected}")
    return errors


def _run_tests(paths: tuple[str, ...]) -> int:
    python = ROOT / ".venv" / "bin" / "python"
    executable = str(python) if python.is_file() else sys.executable
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "")
    return subprocess.call(
        [executable, "-m", "pytest", "-q", "--tb=short", "-n", "0", *paths],
        cwd=ROOT,
        env=env,
    )


def check_gate(gate_id: str, *, allow_planned: bool = False) -> int:
    errors = validate_packet(allow_planned=allow_planned)
    if gate_id not in EXPECTED_GATES:
        errors.append(f"unknown gate {gate_id}")
    if not (ROOT / RELEASE_EVIDENCE_TEST).is_file():
        errors.append(f"missing release evidence corpus: {RELEASE_EVIDENCE_TEST}")
    for path in GATE_TESTS.get(gate_id, ()):
        if not (ROOT / path).is_file():
            errors.append(f"missing evidence test: {path}")
    state = _state(gate_id)
    if state not in {"Planned", "Implemented", "Verified", "Deferred", "Blocked"}:
        errors.append(f"{gate_id} has invalid state {state!r}")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    if state == "Verified" or os.environ.get("HEDRON_GATE_VERIFY") == "1":
        paths = GATE_TESTS[gate_id]
        if RELEASE_EVIDENCE_TEST not in paths:
            paths = (*paths, RELEASE_EVIDENCE_TEST)
        return _run_tests(paths)
    print(f"ok: {gate_id} ({state}; executable evidence is not yet claimed)")
    return 0
