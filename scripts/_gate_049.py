"""Shared constants and contract helpers for the phase 0.49 gate."""

from __future__ import annotations

from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.49.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "fastapi-pydantic-capability-inventory-049.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_49.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-049.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "FASTAPI_PYDANTIC_CONVERGENCE_049.md"
API = ROOT / "docs" / "api" / "FASTAPI_PYDANTIC_CONVERGENCE.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0076-FASTAPI-PYDANTIC-CONVERGENCE.md"
LIFETIME = ROOT / "docs" / "acceptance" / "fastapi-lifetime-049.toml"
BINDING = ROOT / "docs" / "acceptance" / "fastapi-binding-049.toml"
TYPESCHEMA_V2 = ROOT / "docs" / "acceptance" / "typeschema-v2-049.toml"
UNIONS = ROOT / "docs" / "acceptance" / "fastapi-unions-openapi-049.toml"
SETTINGS = ROOT / "docs" / "acceptance" / "fastapi-settings-research-049.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#380"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    LIFETIME,
    BINDING,
    TYPESCHEMA_V2,
    UNIONS,
    SETTINGS,
)

EXPECTED_GATES = (
    "LIFETIME-049",
    "BINDING-049",
    "SCHEMA-049",
    "UNION-049",
    "ROUTER-049",
    "OPENAPI-049",
    "SECURITY-049",
    "ADAPTER-VALIDATION-049",
    "SETTINGS-049",
    "RESEARCH-049",
    "A11Y-049",
    "PERF-049",
    "COMPAT-049",
    "DOCS-049",
    "REGRESS-049",
    "PKG-049",
)
EXPECTED_REQUIREMENT_RANGES = (
    "FP-LIFETIME-001..008",
    "FP-BIND-001..012",
    "FP-SCHEMA-001..012",
    "FP-UNION-001..010",
    "FP-OPENAPI-001..014",
    "FP-ADAPTER-001..008",
    "FP-SETTINGS-001..008",
    "FP-RESEARCH-001..006",
    "FP-EXCLUDE-001..010",
)
EVALUATE_REQUIREMENT_IDS = frozenset({"FP-SETTINGS-001..008"})
EXPERIMENTAL_REQUIREMENT_IDS = frozenset({"FP-RESEARCH-001..006"})
EXCLUDED_REQUIREMENT_IDS = frozenset({"FP-EXCLUDE-001..010"})

FROZEN_CONTRACT_MARKERS = (
    'Depends(scope="function")',
    'Depends(scope="request")',
    "BoundaryBindingPlan",
    "BindingPlan",
    "apply_modeled_signature",
    "RESEARCH-049",
    "RequiresScopes",
    "TypeSchema",
)

GATE_TESTS: dict[str, list[str]] = {
    "LIFETIME-049": ["tests/unit/test_lifetime_049.py"],
    "BINDING-049": ["tests/unit/test_binding_049.py"],
    "SCHEMA-049": ["tests/unit/test_schema_049.py"],
    "UNION-049": ["tests/unit/test_union_049.py"],
    "ROUTER-049": ["tests/unit/test_router_049.py"],
    "OPENAPI-049": ["tests/unit/test_openapi_049.py"],
    "SECURITY-049": ["tests/unit/test_security_049.py"],
    "ADAPTER-VALIDATION-049": ["tests/unit/test_adapter_validation_049.py"],
    "SETTINGS-049": ["tests/unit/test_settings_049.py"],
    "RESEARCH-049": ["tests/unit/test_research_049.py"],
    "A11Y-049": ["tests/browser/test_a11y_049.py"],
    "PERF-049": ["tests/unit/test_perf_049.py"],
    "COMPAT-049": ["tests/unit/test_compat_049.py"],
    "DOCS-049": ["tests/unit/test_docs_049.py"],
    "REGRESS-049": ["tests/unit/test_compat_049.py"],
    "PKG-049": ["tests/unit/test_pkg_049.py"],
}


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-081 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-084 | Accepted |" in decisions and all(
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
        errors.append("RFC-0076 and D-081 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-084 and the frozen 0.49 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.49.toml")
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
