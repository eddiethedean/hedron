"""Shared constants and contract helpers for the phase 0.50 gate."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.50.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "explorer-capability-inventory-050.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_50.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-050.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "EXPLORER_050.md"
API = ROOT / "docs" / "api" / "EXPLORER_ARCHITECTURE.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0077-EXPLORER-ARCHITECTURE.md"
ARCHITECTURE = ROOT / "docs" / "acceptance" / "explorer-architecture-050.toml"
PROVIDER = ROOT / "docs" / "acceptance" / "explorer-provider-050.toml"
QUERY = ROOT / "docs" / "acceptance" / "explorer-query-050.toml"
DIFF = ROOT / "docs" / "acceptance" / "explorer-diff-050.toml"
LAB = ROOT / "docs" / "acceptance" / "explorer-lab-050.toml"
HEADLESS = ROOT / "docs" / "acceptance" / "explorer-headless-050.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#501"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    ARCHITECTURE,
    PROVIDER,
    QUERY,
    DIFF,
    LAB,
    HEADLESS,
)

EXPECTED_GATES = (
    "ARCH-050",
    "PROVIDER-050",
    "CONSUME-050",
    "QUERY-050",
    "DIFF-050",
    "LAB-050",
    "HEADLESS-050",
    "ECOSYSTEM-050",
    "SECURITY-050",
    "PRIVACY-050",
    "A11Y-050",
    "BROWSER-050",
    "PERF-050",
    "RESILIENCE-050",
    "DOCS-050",
    "COMPAT-050",
    "PKG-050",
    "REGRESS-050",
)
EXPECTED_REQUIREMENT_RANGES = (
    "EXP-ARCH-001..005",
    "EXP-PROVIDER-001..005",
    "EXP-CONSUME-001..004",
    "EXP-QUERY-001..004",
    "EXP-DIFF-001..004",
    "EXP-LAB-001..003",
    "EXP-HEADLESS-001..004",
    "EXP-ECOSYSTEM-001..004",
    "EXP-SECURITY-001..004",
    "EXP-PRIVACY-001..003",
    "EXP-A11Y-001..003",
    "EXP-BROWSER-001..003",
    "EXP-PERF-001..003",
    "EXP-RESILIENCE-001..003",
    "EXP-DOCS-001..003",
    "EXP-COMPAT-001..003",
    "EXP-PKG-001..002",
    "EXP-REGRESS-001..002",
    "EXP-EXCLUDE-001..008",
)
EVALUATE_REQUIREMENT_IDS: frozenset[str] = frozenset()
EXPERIMENTAL_REQUIREMENT_IDS: frozenset[str] = frozenset()
EXCLUDED_REQUIREMENT_IDS = frozenset({"EXP-EXCLUDE-001..008"})

FROZEN_CONTRACT_MARKERS = (
    "ExplorerPanelMeta",
    "register_explorer_panel",
    "explorer_router",
    "/hedron-explorer/",
    "ExplorerProvider",
    "diagnostics_to_sarif",
    "EXPLORER-10-001",
    "REV-026-003",
)

GATE_TESTS: dict[str, list[str]] = {
    "ARCH-050": ["tests/unit/test_architecture_050.py"],
    "PROVIDER-050": ["tests/unit/test_provider_050.py"],
    "CONSUME-050": ["tests/unit/test_consume_050.py"],
    "QUERY-050": ["tests/unit/test_query_050.py"],
    "DIFF-050": ["tests/unit/test_diff_050.py"],
    "LAB-050": ["tests/unit/test_lab_050.py"],
    "HEADLESS-050": ["tests/unit/test_headless_050.py"],
    "ECOSYSTEM-050": ["tests/unit/test_ecosystem_050.py"],
    "SECURITY-050": ["tests/unit/test_security_050.py"],
    "PRIVACY-050": ["tests/unit/test_privacy_050.py"],
    "A11Y-050": ["tests/browser/test_a11y_050.py"],
    "BROWSER-050": ["tests/browser/test_browser_050.py"],
    "PERF-050": ["tests/unit/test_perf_050.py"],
    "RESILIENCE-050": ["tests/unit/test_resilience_050.py"],
    "DOCS-050": ["tests/unit/test_docs_050.py"],
    "COMPAT-050": ["tests/unit/test_compat_050.py"],
    "PKG-050": ["tests/unit/test_pkg_050.py"],
    "REGRESS-050": [
        "tests/unit/test_regress_050.py",
        "tests/unit/test_authoring_050.py",
    ],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-085 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-086 | Accepted |" in decisions and all(
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
        errors.append("RFC-0077 and D-085 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-086 and the frozen 0.50 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.50.toml")
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
