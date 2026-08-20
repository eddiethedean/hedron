"""Shared constants for the phase 0.52 conformance / Posit gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.52.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "conformance-capability-inventory-052.toml"
PROFILE = ROOT / "docs" / "acceptance" / "conformance-profile-052.toml"
POSIT = ROOT / "docs" / "acceptance" / "posit-lifecycle-052.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_52.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-052.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "CONFORMANCE_052.md"
POSIT_IMPLEMENTATION = ROOT / "docs" / "implementation" / "POSIT_LIFECYCLE_052.md"
API = ROOT / "docs" / "api" / "CONFORMANCE.md"
POSIT_API = ROOT / "docs" / "api" / "POSIT_LIFECYCLE.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0079-CONFORMANCE-AUTHORITY-POSIT-LIFECYCLE.md"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#522"
PREDECESSOR = "0.51.2"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PROFILE,
    POSIT,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    POSIT_IMPLEMENTATION,
    API,
    POSIT_API,
    RFC,
)

EXPECTED_GATES = (
    "PROTOCOL-052",
    "PROFILE-052",
    "FIXTURE-052",
    "NEGATIVE-052",
    "RUNTIME-052",
    "DIFF-052",
    "SECURITY-052",
    "SANDBOX-052",
    "REPORT-052",
    "CI-052",
    "COMPAT-052",
    "PLATFORM-052",
    "COOKIE-052",
    "CONTEXT-052",
    "HANDSOFF-052",
    "MATRIX-052",
    "PDIAG-052",
    "ROUTEURL-052",
    "DOCS-052",
    "AUTHOR-052",
    "PKG-052",
    "SUPPLY-052",
    "REGRESS-052",
)

FROZEN_CONTRACT_MARKERS = (
    "hedron-portable-1",
    "CONTRACT_VERSION",
    "load_bundled_fixtures",
    "Capability",
    "HedronPosit",
    "cookie_path_for_mount",
    "ConnectCookieMode",
    "PositContext",
    "href_for",
    "drop_supported",
)

GATE_TESTS: dict[str, list[str]] = {
    "PROTOCOL-052": ["tests/unit/test_protocol_052.py"],
    "PROFILE-052": ["tests/unit/test_profile_052.py"],
    "FIXTURE-052": ["tests/unit/test_fixture_052.py"],
    "NEGATIVE-052": ["tests/unit/test_negative_052.py"],
    "RUNTIME-052": ["tests/unit/test_runtime_052.py"],
    "DIFF-052": ["tests/unit/test_diff_052.py"],
    "SECURITY-052": ["tests/unit/test_security_052.py"],
    "SANDBOX-052": ["tests/unit/test_sandbox_052.py"],
    "REPORT-052": ["tests/unit/test_report_052.py"],
    "CI-052": ["tests/unit/test_ci_052.py"],
    "COMPAT-052": ["tests/unit/test_compat_052.py"],
    "PLATFORM-052": ["tests/unit/test_platform_052.py"],
    "COOKIE-052": ["tests/unit/test_cookie_052.py"],
    "CONTEXT-052": ["tests/unit/test_context_052.py"],
    "HANDSOFF-052": ["tests/unit/test_handsoff_052.py"],
    "MATRIX-052": ["tests/unit/test_matrix_052.py"],
    "PDIAG-052": ["tests/unit/test_pdiag_052.py"],
    "ROUTEURL-052": ["tests/unit/test_routeurl_052.py"],
    "DOCS-052": ["tests/unit/test_docs_052.py"],
    "AUTHOR-052": ["tests/unit/test_author_052.py"],
    "PKG-052": ["tests/unit/test_pkg_052.py"],
    "SUPPLY-052": ["tests/unit/test_supply_052.py"],
    "REGRESS-052": ["tests/unit/test_regress_052.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-089 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (RFC, IMPLEMENTATION, POSIT_IMPLEMENTATION, API, POSIT_API, PACKET)
    )
    return "| D-090 | Accepted |" in decisions and all(
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
        errors.append("RFC-0079 and D-089 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-090 and the frozen 0.52 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.52.toml")
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
