"""Shared constants for the phase 0.55 workflow gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.55.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "workflow-inventory-055.toml"
CONTRACT = ROOT / "docs" / "acceptance" / "workflow-contract-055.toml"
PARITY = ROOT / "docs" / "acceptance" / "workflow-parity-055.toml"
UPGRADE = ROOT / "docs" / "acceptance" / "workflow-upgrade-055.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_55.md"
UPGRADE_FIXTURES = ROOT / "docs" / "acceptance" / "upgrade-fixtures-055.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "WORKFLOW_055.md"
API = ROOT / "docs" / "api" / "WORKFLOW.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0082-SECURE-UPGRADEABLE-WORKFLOWS.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#544"
PREDECESSOR = "0.54.0"

PACKET_FILES = (
    GATE,
    INVENTORY,
    CONTRACT,
    PARITY,
    UPGRADE,
    PACKET,
    UPGRADE_FIXTURES,
    IMPLEMENTATION,
    API,
    RFC,
)

EXPECTED_GATES = (
    "CONTRACT-055",
    "LAYOUT-055",
    "CAP-055",
    "REPLAY-055",
    "UPLOAD-055",
    "CSP-055",
    "UPGRADE-055",
    "PARITY-055",
    "REGRESS-055",
    "PKG-055",
)

FROZEN_CONTRACT_MARKERS = (
    "hedron.workflow",
    "MasterDetail",
    "CapabilityProvider",
    "IdempotencyPolicy",
    "UploadField",
    "NonceContext",
    "upgrade-report",
    "SecurityPolicy",
    "AppShell",
)

GATE_TESTS: dict[str, list[str]] = {
    "CONTRACT-055": ["tests/unit/test_contract_055.py"],
    "LAYOUT-055": ["tests/unit/test_layout_055.py"],
    "CAP-055": ["tests/unit/test_cap_055.py"],
    "REPLAY-055": ["tests/unit/test_replay_055.py"],
    "UPLOAD-055": ["tests/unit/test_upload_055.py"],
    "CSP-055": ["tests/unit/test_csp_055.py"],
    "UPGRADE-055": ["tests/unit/test_upgrade_055.py"],
    "PARITY-055": ["tests/unit/test_parity_055.py"],
    "REGRESS-055": ["tests/unit/test_regress_055.py"],
    "PKG-055": ["tests/unit/test_pkg_055.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-095 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-096 | Accepted |" in decisions and all(
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
        errors.append("RFC-0082 and D-095 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-096 and the frozen 0.55 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.55.toml")
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
