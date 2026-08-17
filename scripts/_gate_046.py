"""Shared constants and contract helpers for the phase 0.46 gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.46.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "package-workflow-capability-inventory-046.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_46.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-046.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "PACKAGE_NATIVE_WORKFLOWS_046.md"
API = ROOT / "docs" / "api" / "PACKAGE_WORKFLOWS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0073-PACKAGE-NATIVE-WORKFLOWS.md"
FEATURE_BUNDLE = ROOT / "docs" / "acceptance" / "feature-bundle-046.toml"
DATA_WORKSPACE = ROOT / "docs" / "acceptance" / "data-workspace-046.toml"
CHART_INTERACTION = ROOT / "docs" / "acceptance" / "chart-interaction-046.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#334"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    FEATURE_BUNDLE,
    DATA_WORKSPACE,
    CHART_INTERACTION,
)

EXPECTED_GATES = (
    "BUNDLE-046",
    "DATAFLOW-046",
    "VISUAL-046",
    "ELEMENT-046",
    "REMOTE-046",
    "WORKBENCH-046",
    "SCENARIO-046",
    "ADAPTER-046",
    "SECURITY-046",
    "A11Y-046",
    "BROWSER-046",
    "COMPAT-046",
    "PERF-046",
    "DOCS-046",
    "REGRESS-046",
    "PKG-046",
)
EXPECTED_REQUIREMENT_RANGES = (
    "PW-BUNDLE-001..010",
    "PW-DATA-001..012",
    "PW-VISUAL-001..010",
    "PW-ELEMENT-001..009",
    "PW-REMOTE-001..010",
    "PW-WORKBENCH-001..010",
    "PW-SCENARIO-001..009",
    "PW-HOST-001..006",
    "PW-SEC-001..010",
    "PW-A11Y-001..007",
    "PW-QUAL-001..006",
    "PW-QUAL-007..008",
    "PW-QUAL-009",
    "PW-QUAL-010",
    "PW-QUAL-011..012",
)

FROZEN_CONTRACT_MARKERS = (
    "InteractionCatalog",
    "PackageProjection",
    "descriptor_fingerprint",
    "hedron.type",
    "Hedron.interactions",
    "DataEditorSource",
    "hedron-chart",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-075 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-079 | Accepted |" in decisions and all(
        marker in combined for marker in FROZEN_CONTRACT_MARKERS
    )


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


GATE_TESTS: dict[str, list[str]] = {
    "BUNDLE-046": ["tests/unit/test_bundles_046.py"],
    "DATAFLOW-046": ["tests/unit/test_workspace_046.py"],
    "VISUAL-046": ["tests/unit/test_chart_interaction_046.py"],
    "ELEMENT-046": ["tests/unit/test_elements_046.py"],
    "REMOTE-046": ["tests/unit/test_remote_046.py"],
    "WORKBENCH-046": ["tests/unit/test_workbench_046.py"],
    "SCENARIO-046": ["tests/unit/test_scenario_046.py"],
    "ADAPTER-046": ["tests/adapters/test_hosts_046.py"],
    "SECURITY-046": ["tests/security/test_security_046.py"],
    "A11Y-046": ["tests/a11y/test_a11y_046.py"],
    "BROWSER-046": ["tests/browser/test_browser_046.py"],
    "COMPAT-046": ["tests/unit/test_compat_046.py"],
    "PERF-046": ["tests/performance/test_perf_046.py"],
    "DOCS-046": ["tests/unit/test_docs_046.py"],
    "REGRESS-046": ["tests/unit/test_regress_046.py"],
    "PKG-046": ["tests/unit/test_phase046_packet.py"],
}


def run_pytest(paths: list[str]) -> int:
    import subprocess

    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0073 and D-075 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-079 and the frozen 0.46 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.46.toml")
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
