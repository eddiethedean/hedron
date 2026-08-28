"""Shared constants and contract helpers for the phase 0.44 gate."""

from __future__ import annotations

import subprocess
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.44.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "type-authoring-capability-inventory-044.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_44.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-044.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "TYPE_DRIVEN_AUTHORING_044.md"
API = ROOT / "docs" / "api" / "TYPE_DRIVEN_AUTHORING.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0071-TYPE-DRIVEN-AUTHORING.md"
FORM_INVENTORY = ROOT / "docs" / "acceptance" / "type-form-inventory-044.toml"
TYPE_SCHEMA = ROOT / "docs" / "acceptance" / "type-schema-044.toml"
ADAPTERS = ROOT / "docs" / "acceptance" / "adapter-disposition-044.toml"
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
    FORM_INVENTORY,
    TYPE_SCHEMA,
    ADAPTERS,
)
TRACKING_ISSUE = "#318"

EXPECTED_GATES = (
    "MODEL-044",
    "TYPING-044",
    "FORM-044",
    "EFFECT-044",
    "CLASS-044",
    "SCHEMA-044",
    "SECURITY-044",
    "A11Y-044",
    "BROWSER-044",
    "TOOLING-044",
    "COMPAT-044",
    "PERF-044",
    "DOCS-044",
    "REGRESS-044",
    "PKG-044",
)
EXPECTED_REQUIREMENT_RANGES = (
    "TA-MODEL-001..011",
    "TA-MARKER-001..008",
    "TA-HANDLE-001..007",
    "TA-FORM-001..009",
    "TA-EFFECT-001..009",
    "TA-CLASS-001..009",
    "TA-SCHEMA-001..006",
    "TA-SEC-001..008",
    "TA-A11Y-001..006",
    "TA-DX-001..008",
    "TA-QUAL-001..006",
    "TA-QUAL-011",
    "TA-QUAL-007..008",
    "TA-QUAL-009",
    "TA-QUAL-010",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-072 | Accepted |" in decisions


def cross_phase_refinement_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-076 | Accepted |" in decisions and all(
        marker in combined
        for marker in (
            "ViewParams",
            "FormBody",
            "hedron.type",
            "OutcomeMap(case(",
            "BindingAdapter",
        )
    )


GATE_TESTS: dict[str, list[str]] = {
    "MODEL-044": ["tests/unit/test_models_044.py"],
    "TYPING-044": ["tests/unit/test_typing_044.py"],
    "FORM-044": ["tests/unit/test_forms_044.py"],
    "EFFECT-044": ["tests/unit/test_effects_044.py"],
    "CLASS-044": ["tests/unit/test_class_handlers_044.py"],
    "SCHEMA-044": ["tests/unit/test_type_schema_044.py"],
    "SECURITY-044": ["tests/security/test_security_044.py"],
    "A11Y-044": ["tests/a11y/test_a11y_044.py"],
    "BROWSER-044": ["tests/browser/test_browser_044.py"],
    "TOOLING-044": ["tests/unit/test_tooling_044.py"],
    "COMPAT-044": ["tests/unit/test_compat_044.py"],
    "PERF-044": ["tests/performance/test_perf_044.py"],
    "DOCS-044": ["tests/unit/test_docs_044.py"],
    "REGRESS-044": ["tests/unit/test_regress_044.py"],
    "PKG-044": ["tests/unit/test_phase044_packet.py"],
}


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
    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0071 and D-072 must remain Accepted")
    if not cross_phase_refinement_present():
        errors.append("D-076 and the frozen 0.44 contract markers must remain present")
    if TRACKING_ISSUE not in PACKET.read_text(encoding="utf-8"):
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.44.toml")
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
