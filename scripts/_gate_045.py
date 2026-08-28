"""Shared constants and contract helpers for the phase 0.45 gate."""

from __future__ import annotations

import subprocess
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.45.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "ecosystem-capability-inventory-045.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_45.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-045.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "TYPED_INTERACTION_ECOSYSTEM_045.md"
API = ROOT / "docs" / "api" / "INTERACTION_CATALOG.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0072-TYPED-INTERACTION-ECOSYSTEM.md"
CATALOG_ENTRY = ROOT / "docs" / "acceptance" / "catalog-entry-045.toml"
MANIFEST_FORMAT = ROOT / "docs" / "acceptance" / "manifest-format-045.toml"
HOST_FACTS = ROOT / "docs" / "acceptance" / "host-portable-facts-045.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    CATALOG_ENTRY,
    MANIFEST_FORMAT,
    HOST_FACTS,
)
TRACKING_ISSUE = "#328"

EXPECTED_GATES = (
    "CATALOG-045",
    "MANIFEST-045",
    "PROJECTION-045",
    "HOST-045",
    "AUTHOR-045",
    "SURFACE-045",
    "REMOTE-045",
    "TOOLING-045",
    "PORTABLE-045",
    "DEPLOY-045",
    "SECURITY-045",
    "A11Y-045",
    "BROWSER-045",
    "COMPAT-045",
    "PERF-045",
    "DOCS-045",
    "REGRESS-045",
    "PKG-045",
)
EXPECTED_REQUIREMENT_RANGES = (
    "EC-CAT-001..010",
    "EC-MAN-001..010",
    "EC-PROJ-001..010",
    "EC-HOST-001..008",
    "EC-AUTHOR-001..008",
    "EC-SURFACE-001..008",
    "EC-REMOTE-001..008",
    "EC-TOOL-001..010",
    "EC-PORT-001..009",
    "EC-DEPLOY-001..007",
    "EC-SEC-001..010",
    "EC-A11Y-001..006",
    "EC-QUAL-001..006",
    "EC-QUAL-007..008",
    "EC-QUAL-009",
    "EC-QUAL-010",
    "EC-QUAL-011..012",
)

FROZEN_CONTRACT_MARKERS = (
    "ViewParams",
    "FormBody",
    "hedron.type",
    "OutcomeMap(case(",
    "BindingAdapter",
    "descriptor_fingerprint",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-074 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-077 | Accepted |" in decisions and all(
        marker in combined for marker in FROZEN_CONTRACT_MARKERS
    )


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing required file: {path}")


GATE_TESTS: dict[str, list[str]] = {
    "CATALOG-045": ["tests/unit/test_catalog_045.py"],
    "MANIFEST-045": ["tests/unit/test_manifest_045.py"],
    "PROJECTION-045": ["tests/unit/test_projections_045.py"],
    "HOST-045": ["tests/adapters/test_hosts_045.py"],
    "AUTHOR-045": ["tests/unit/test_authoring_045.py"],
    "SURFACE-045": ["tests/unit/test_surfaces_045.py"],
    "REMOTE-045": ["tests/unit/test_remote_045.py"],
    "TOOLING-045": ["tests/unit/test_tooling_045.py"],
    "PORTABLE-045": [
        "tests/unit/test_portable_045.py",
        "tests/conformance/test_catalog_045.py",
    ],
    "DEPLOY-045": ["tests/unit/test_deploy_045.py"],
    "SECURITY-045": ["tests/security/test_security_045.py"],
    "A11Y-045": ["tests/a11y/test_a11y_045.py"],
    "BROWSER-045": ["tests/browser/test_browser_045.py"],
    "COMPAT-045": ["tests/unit/test_compat_045.py"],
    "PERF-045": ["tests/performance/test_perf_045.py"],
    "DOCS-045": ["tests/unit/test_docs_045.py"],
    "REGRESS-045": ["tests/unit/test_regress_045.py"],
    "PKG-045": ["tests/unit/test_phase045_packet.py"],
}


def gate_state(gate_id: str) -> str | None:
    data = tomllib.loads(GATE.read_text(encoding="utf-8"))
    for row in data.get("evidence") or []:
        if row.get("id") == gate_id:
            return str(row.get("state", "")).strip()
    return None


def run_pytest(paths: list[str]) -> int:
    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0072 and D-074 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-077 and the frozen 0.45 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.45.toml")
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
