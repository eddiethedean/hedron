"""Shared constants for the phase 0.53 application DX gate."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.53.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "application-dx-inventory-053.toml"
ASSETS = ROOT / "docs" / "acceptance" / "application-assets-053.toml"
CONTRACTS = ROOT / "docs" / "acceptance" / "application-contracts-053.toml"
TOOLING = ROOT / "docs" / "acceptance" / "application-tooling-053.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_53.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-053.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "APPLICATION_DX_053.md"
API = ROOT / "docs" / "api" / "APPLICATION_DX.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0080-APPLICATION-DX-CONTRACTS.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#514"
PREDECESSOR = "0.52.0"

PACKET_FILES = (
    GATE,
    INVENTORY,
    ASSETS,
    CONTRACTS,
    TOOLING,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
)

EXPECTED_GATES = (
    "ASSET-053",
    "DIAG-053",
    "ROUTE-053",
    "WORKFLOW-053",
    "TESTGEN-053",
    "THEME-053",
    "DISCOVER-053",
    "FLEET-053",
    "DOCS-053",
    "PKG-053",
    "REGRESS-053",
)

FROZEN_CONTRACT_MARKERS = (
    "inject_page_assets",
    "AssetRef",
    "Diagnostic",
    "Suppression",
    "RouteMeta",
    "routes_json",
    "JobBackend",
    "JobState",
    "InteractionCatalog",
    "Theme",
    "REQUIRED_A11Y_TOKENS",
    "hedron.__all__",
)

GATE_TESTS: dict[str, list[str]] = {
    "ASSET-053": ["tests/unit/test_asset_053.py"],
    "DIAG-053": ["tests/unit/test_diag_053.py"],
    "ROUTE-053": ["tests/unit/test_route_053.py"],
    "WORKFLOW-053": ["tests/unit/test_workflow_053.py"],
    "TESTGEN-053": ["tests/unit/test_testgen_053.py"],
    "THEME-053": ["tests/unit/test_theme_053.py"],
    "DISCOVER-053": ["tests/unit/test_discover_053.py"],
    "FLEET-053": ["tests/unit/test_fleet_053.py"],
    "DOCS-053": ["tests/unit/test_docs_053.py"],
    "PKG-053": ["tests/unit/test_pkg_053.py"],
    "REGRESS-053": ["tests/unit/test_regress_053.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-091 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-092 | Accepted |" in decisions and all(
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
    import subprocess
    import sys

    command = [sys.executable, "-m", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0080 and D-091 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-092 and the frozen 0.53 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.53.toml")
    elif state not in {"Planned", "Implemented", "Verified", "Deferred", "Excluded"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    tests = GATE_TESTS.get(gate_id, [])
    if state in {"Verified", "Deferred", "Excluded"} and not tests:
        errors.append(f"{gate_id} is {state} but has no executable evidence tests bound")
    if errors:
        for message in errors:
            print(f"{gate_id}: {message}", flush=True)
        return 1
    # Evidence tests run only when the gate is Verified (Stage 1+).
    if state == "Verified" and tests:
        code = run_pytest(tests)
        if code:
            return code
    print(f"ok: {gate_id}")
    return 0
