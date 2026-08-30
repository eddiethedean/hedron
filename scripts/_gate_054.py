"""Shared constants for the phase 0.54 authoring-loop and chrome gate."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.54.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "authoring-loop-inventory-054.toml"
SHARED = ROOT / "docs" / "acceptance" / "authoring-shared-054.toml"
SIM_NOTEBOOK = ROOT / "docs" / "acceptance" / "authoring-sim-notebook-054.toml"
CHROME = ROOT / "docs" / "acceptance" / "authoring-chrome-054.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_54.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-054.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "AUTHORING_LOOP_054.md"
API = ROOT / "docs" / "api" / "AUTHORING_LOOP.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0081-AUTHORING-LOOP-AND-CHROME.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#538"
PREDECESSOR = "0.53.0"

PACKET_FILES = (
    GATE,
    INVENTORY,
    SHARED,
    SIM_NOTEBOOK,
    CHROME,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
)

EXPECTED_GATES = (
    "SAMPLE-054",
    "DOCTOR-054",
    "SIM-054",
    "PARITY-054",
    "NOTEBOOK-054",
    "LIFECYCLE-054",
    "SECURITY-054",
    "TOPOLOGY-054",
    "ECOSYSTEM-054",
    "COMPAT-054",
    "PLATFORM-054",
    "A11Y-054",
    "DOCS-054",
    "PKG-054",
    "REGRESS-054",
)

FROZEN_CONTRACT_MARKERS = (
    "hedron_conformance.authoring_loop",
    "SimApp",
    "UnsupportedSimFeatureError",
    "start_preview",
    "NotebookPreview",
    "package_doctor",
    "Theme",
    "AppShell",
    "hedron package doctor",
)

GATE_TESTS: dict[str, list[str]] = {
    "SAMPLE-054": ["tests/unit/test_sample_054.py"],
    "DOCTOR-054": ["tests/unit/test_doctor_054.py"],
    "SIM-054": ["tests/unit/test_sim_054.py"],
    "PARITY-054": ["tests/unit/test_parity_054.py"],
    "NOTEBOOK-054": ["tests/unit/test_notebook_054.py"],
    "LIFECYCLE-054": ["tests/unit/test_lifecycle_054.py"],
    "SECURITY-054": ["tests/unit/test_security_054.py"],
    "TOPOLOGY-054": ["tests/unit/test_topology_054.py"],
    "ECOSYSTEM-054": ["tests/unit/test_ecosystem_054.py"],
    "COMPAT-054": ["tests/unit/test_compat_054.py"],
    "PLATFORM-054": ["tests/unit/test_platform_054.py"],
    "A11Y-054": ["tests/unit/test_a11y_054.py"],
    "DOCS-054": ["tests/unit/test_docs_054.py"],
    "PKG-054": ["tests/unit/test_pkg_054.py"],
    "REGRESS-054": ["tests/unit/test_regress_054.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-093 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-094 | Accepted |" in decisions and all(
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
        errors.append("RFC-0081 and D-093 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-094 and the frozen 0.54 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.54.toml")
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
