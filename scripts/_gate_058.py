"""Shared constants for the phase 0.58 progressive feature and styling gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.58.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "progressive-authoring-inventory-058.toml"
STYLING_INVENTORY = ROOT / "docs" / "acceptance" / "styling-authoring-inventory-058.toml"
LOWERING = ROOT / "docs" / "acceptance" / "progressive-lowering-058.toml"
STYLING_LOWERING = ROOT / "docs" / "acceptance" / "styling-lowering-058.toml"
EXPLANATION = ROOT / "docs" / "acceptance" / "feature-explanation-058.toml"
DESIGN_SCHEMA = ROOT / "docs" / "acceptance" / "design-system-schema-058.toml"
RECIPE_CATALOG = ROOT / "docs" / "acceptance" / "style-recipe-catalog-058.toml"
TRACKING = ROOT / "docs" / "acceptance" / "progressive-tracking-058.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_58.md"
UPGRADE_FIXTURES = ROOT / "docs" / "acceptance" / "upgrade-fixtures-058.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "PROGRESSIVE_AUTHORING_058.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0085-PROGRESSIVE-FEATURE-AUTHORING.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
DOCS_STATUS = ROOT / "docs" / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"
WHATS_NEW = ROOT / "docs" / "guides" / "whats-new-0.58.md"

PREDECESSOR = "0.57.0"
PLANNING_BASELINE = "v0.57.0"
RELEASE_CANDIDATE = "0.58.0"

PACKET_FILES = (
    GATE,
    INVENTORY,
    STYLING_INVENTORY,
    LOWERING,
    STYLING_LOWERING,
    EXPLANATION,
    DESIGN_SCHEMA,
    RECIPE_CATALOG,
    TRACKING,
    PACKET,
    UPGRADE_FIXTURES,
    IMPLEMENTATION,
    RFC,
)

EXPECTED_GATES = (
    "CONTRACT-058",
    "LOWER-058",
    "SCREEN-058",
    "FORM-058",
    "RESOURCE-058",
    "TASK-058",
    "DASH-058",
    "FLOW-058",
    "BRAND-058",
    "THEME-058",
    "RECIPE-058",
    "SCOPE-058",
    "EXPLAIN-058",
    "VISUAL-058",
    "A11Y-058",
    "SECURITY-058",
    "ADAPTER-058",
    "REGRESS-058",
    "DX-058",
    "PKG-058",
)

FROZEN_CONTRACT_MARKERS = (
    "Hedron.screen",
    "Hedron.form_command",
    "DataWorkspace.with_screen",
    "TaskFlow",
    "DashboardWorkspace",
    "SessionAuthFlow",
    "UploadFlow",
    "DesignSystem",
    "StyleRecipe",
    "StyleScope",
    "W0",
    "W17",
)

GATE_TESTS: dict[str, list[str]] = {
    "CONTRACT-058": ["tests/unit/test_contract_058.py"],
    "LOWER-058": ["tests/unit/test_lower_058.py"],
    "SCREEN-058": ["tests/unit/test_screen_058.py"],
    "FORM-058": ["tests/unit/test_form_058.py"],
    "RESOURCE-058": ["tests/unit/test_resource_058.py"],
    "TASK-058": ["tests/unit/test_task_058.py"],
    "DASH-058": ["tests/unit/test_dash_058.py"],
    "FLOW-058": ["tests/unit/test_flow_058.py"],
    "BRAND-058": ["tests/unit/test_brand_058.py"],
    "THEME-058": ["tests/unit/test_theme_058.py"],
    "RECIPE-058": ["tests/unit/test_recipe_058.py"],
    "SCOPE-058": ["tests/unit/test_scope_058.py"],
    "EXPLAIN-058": ["tests/unit/test_explain_058.py"],
    "VISUAL-058": ["tests/unit/test_visual_058.py"],
    "A11Y-058": ["tests/unit/test_a11y_058.py"],
    "SECURITY-058": ["tests/unit/test_security_058.py"],
    "ADAPTER-058": ["tests/unit/test_adapter_058.py"],
    "REGRESS-058": ["tests/unit/test_regress_058.py"],
    "DX-058": ["tests/unit/test_dx_058.py"],
    "PKG-058": ["tests/unit/test_pkg_058.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-101 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, PACKET)
    )
    return (
        "| D-102 | Accepted |" in decisions
        and "| D-105 | Accepted |" in decisions
        and all(marker in combined for marker in FROZEN_CONTRACT_MARKERS)
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


def run_pytest(paths: list[str]) -> int:
    import os
    import subprocess
    import sys

    venv_python = ROOT / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.is_file() else sys.executable
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "")
    command = [
        python,
        "-m",
        "pytest",
        "-q",
        "--tb=short",
        "-n",
        "0",
        *paths,
    ]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT, env=env)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0085 and D-101 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-102 / D-105 and the frozen 0.58 contract markers must remain present")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.58.toml")
    elif state not in {"Planned", "Implemented", "Verified", "Deferred", "Excluded"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    tests = GATE_TESTS.get(gate_id, [])
    if state in {"Verified", "Deferred", "Excluded"} and not tests:
        errors.append(f"{gate_id} is {state} but has no executable evidence tests bound")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    if state == "Verified" and tests:
        code = run_pytest(tests)
        if code:
            return code
    print(f"ok: {gate_id}")
    return 0
