"""Shared constants for the phase 0.51 extras gate."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.51.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "extras-capability-inventory-051.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_51.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-051.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "EXTRAS_051.md"
API = ROOT / "docs" / "api" / "EXTRAS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0078-CURATED-EXTRAS-LIFECYCLE.md"
DESCRIPTOR = ROOT / "docs" / "acceptance" / "extras-descriptor-051.toml"
EXPERIMENTAL = ROOT / "docs" / "acceptance" / "extras-experimental-disposition-051.toml"
WORKBENCH = ROOT / "docs" / "acceptance" / "extras-workbench-051.toml"
LIFECYCLE = ROOT / "docs" / "acceptance" / "extras-lifecycle-051.toml"
COMPANION = ROOT / "docs" / "acceptance" / "extras-companion-authoring-051.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#507"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    DESCRIPTOR,
    EXPERIMENTAL,
    WORKBENCH,
    LIFECYCLE,
    COMPANION,
)

EXPECTED_GATES = (
    "INVENTORY-051",
    "DESCRIPTOR-051",
    "WORKBENCH-051",
    "DATA-051",
    "IMAGE-051",
    "INPUT-051",
    "LIFECYCLE-051",
    "BROWSER-051",
    "SECURITY-051",
    "SUPPLY-051",
    "A11Y-051",
    "VISUAL-051",
    "ECOSYSTEM-051",
    "DOCS-051",
    "PKG-051",
    "REGRESS-051",
)

FROZEN_CONTRACT_MARKERS = (
    "ExtrasFeature",
    "hedron_extras_sandbox",
    "hedron_extras_experimental",
    "HEDRON_EXPERIMENTAL_UI",
    "EXTRAS-025",
    "BrowserPythonSandbox",
    "hedron-extras-composition",
)

GATE_TESTS: dict[str, list[str]] = {
    "INVENTORY-051": ["tests/unit/test_inventory_051.py"],
    "DESCRIPTOR-051": ["tests/unit/test_descriptor_051.py"],
    "WORKBENCH-051": ["tests/unit/test_workbench_051.py"],
    "DATA-051": ["tests/unit/test_data_051.py"],
    "IMAGE-051": ["tests/unit/test_image_051.py"],
    "INPUT-051": ["tests/unit/test_input_051.py"],
    "LIFECYCLE-051": ["tests/unit/test_lifecycle_051.py"],
    "BROWSER-051": ["tests/browser/test_browser_051.py"],
    "SECURITY-051": ["tests/unit/test_security_051.py"],
    "SUPPLY-051": ["tests/unit/test_supply_051.py"],
    "A11Y-051": ["tests/browser/test_a11y_051.py"],
    "VISUAL-051": ["tests/browser/test_visual_051.py"],
    "ECOSYSTEM-051": ["tests/unit/test_ecosystem_051.py"],
    "DOCS-051": ["tests/unit/test_docs_051.py"],
    "PKG-051": ["tests/unit/test_pkg_051.py"],
    "REGRESS-051": ["tests/unit/test_regress_051.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-087 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-088 | Accepted |" in decisions and all(
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
        errors.append("RFC-0078 and D-087 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-088 and the frozen 0.51 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.51.toml")
    elif state not in {"Planned", "Implemented", "Verified", "Deferred", "Excluded"}:
        errors.append(f"{gate_id} unexpected state {state!r}")
    tests = GATE_TESTS.get(gate_id, [])
    if state in {"Verified", "Deferred", "Excluded"} and not tests:
        errors.append(f"{gate_id} is {state} but has no executable evidence tests bound")
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
