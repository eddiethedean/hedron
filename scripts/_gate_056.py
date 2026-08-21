"""Shared constants for the phase 0.56 security control plane gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.56.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "security-inventory-056.toml"
CONTRACT = ROOT / "docs" / "acceptance" / "security-contract-056.toml"
PARITY = ROOT / "docs" / "acceptance" / "security-parity-056.toml"
UPGRADE = ROOT / "docs" / "acceptance" / "security-upgrade-056.toml"
CONTROL_INVENTORY = ROOT / "docs" / "acceptance" / "security-control-inventory-056.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_56.md"
UPGRADE_FIXTURES = ROOT / "docs" / "acceptance" / "upgrade-fixtures-056.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "SECURITY_056.md"
API = ROOT / "docs" / "api" / "SECURITY_PLANE.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0083-SECURITY-CONTROL-PLANE.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
DOCS_STATUS = ROOT / "docs" / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#550"
PREDECESSOR = "0.55.0"

PACKET_FILES = (
    GATE,
    INVENTORY,
    CONTRACT,
    PARITY,
    UPGRADE,
    CONTROL_INVENTORY,
    PACKET,
    UPGRADE_FIXTURES,
    IMPLEMENTATION,
    API,
    RFC,
)

EXPECTED_GATES = (
    "CONTRACT-056",
    "CONFORM-056",
    "SENS-056",
    "CTX-056",
    "POSTURE-056",
    "SINK-056",
    "EGRESS-056",
    "INTENT-056",
    "BUDGET-056",
    "ADVERSARY-056",
    "PERF-056",
    "REGRESS-056",
    "PKG-056",
)

FROZEN_CONTRACT_MARKERS = (
    "SecurityPolicy",
    "SecurityContext",
    "SensitiveLabel",
    "RequestBudget",
    "SignedIntent",
    "SecurityKeyring",
    "SafeUrl",
    "TrustedHtml",
    "security-check",
    "hedron_core.security_plane",
)

GATE_TESTS: dict[str, list[str]] = {
    "CONTRACT-056": ["tests/unit/test_contract_056.py"],
    "CONFORM-056": ["tests/unit/test_conform_056.py"],
    "SENS-056": ["tests/unit/test_sens_056.py"],
    "CTX-056": ["tests/unit/test_ctx_056.py"],
    "POSTURE-056": ["tests/unit/test_posture_056.py"],
    "SINK-056": ["tests/unit/test_sink_056.py"],
    "EGRESS-056": ["tests/unit/test_egress_056.py"],
    "INTENT-056": ["tests/unit/test_intent_056.py"],
    "BUDGET-056": ["tests/unit/test_budget_056.py"],
    "ADVERSARY-056": ["tests/unit/test_adversary_056.py"],
    "PERF-056": ["tests/unit/test_perf_056.py"],
    "REGRESS-056": ["tests/unit/test_regress_056.py"],
    "PKG-056": ["tests/unit/test_pkg_056.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-097 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-098 | Accepted |" in decisions and all(
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
    command = [python, "-m", "pytest", "-q", "--tb=short", "-n", "0", "-p", "no:cacheprovider", *paths]
    # Prefer uv-run isolation when available so system site-packages cannot break evidence.
    uv = ROOT / ".venv" / "bin" / "uv"
    if (ROOT / ".venv" / "bin" / "pytest").is_file():
        command = [
            str(venv_python),
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
        errors.append("RFC-0083 and D-097 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-098 and the frozen 0.56 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.56.toml")
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
