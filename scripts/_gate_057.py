"""Shared constants for the phase 0.57 unified presentation gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.57.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "presentation-inventory-057.toml"
CONTRACT = ROOT / "docs" / "acceptance" / "presentation-contract-057.toml"
PARITY = ROOT / "docs" / "acceptance" / "presentation-parity-057.toml"
ZERO_CSS = ROOT / "docs" / "acceptance" / "zero-css-fixture-057.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_57.md"
UPGRADE_FIXTURES = ROOT / "docs" / "acceptance" / "upgrade-fixtures-057.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "PRESENTATION_057.md"
API = ROOT / "docs" / "api" / "PRESENTATION.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0084-UNIFIED-PRESENTATION.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
DOCS_STATUS = ROOT / "docs" / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#570"
PREDECESSOR = "0.56.0"
PLANNING_BASELINE = "0.56.1"
RELEASE_CANDIDATE = "0.57.0"

PACKET_FILES = (
    GATE,
    INVENTORY,
    CONTRACT,
    PARITY,
    ZERO_CSS,
    PACKET,
    UPGRADE_FIXTURES,
    IMPLEMENTATION,
    API,
    RFC,
)

EXPECTED_GATES = (
    "CONTRACT-057",
    "CSP-057",
    "LAYOUT-057",
    "SURFACE-057",
    "DATA-057",
    "WORKFLOW-057",
    "REGRESS-057",
    "ZERO-CSS-057",
    "PKG-057",
)

FROZEN_CONTRACT_MARKERS = (
    "hedron_core.builtins.appearance",
    "data-hedron-",
    "Surface",
    "GridItem",
    "ResourceList",
    "ResourceRow",
    "Avatar",
    "Identity",
    "Brand",
    "AccountSummary",
    "EnvironmentBanner",
    "NavStatus",
    "AppFooter",
    "plain",
    "raised",
    "zero-application-CSS",
)

GATE_TESTS: dict[str, list[str]] = {
    "CONTRACT-057": ["tests/unit/test_contract_057.py"],
    "CSP-057": ["tests/unit/test_csp_057.py"],
    "LAYOUT-057": ["tests/unit/test_layout_057.py"],
    "SURFACE-057": ["tests/unit/test_surface_057.py"],
    "DATA-057": ["tests/unit/test_data_057.py"],
    "WORKFLOW-057": ["tests/unit/test_workflow_057.py"],
    "REGRESS-057": ["tests/unit/test_regress_057.py"],
    "ZERO-CSS-057": ["tests/unit/test_zero_css_057.py"],
    "PKG-057": ["tests/unit/test_pkg_057.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-099 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-100 | Accepted |" in decisions and all(
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
        errors.append("RFC-0084 and D-099 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-100 and the frozen 0.57 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.57.toml")
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
