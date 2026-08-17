"""Shared constants and contract helpers for the phase 0.47 gate."""

from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.47.toml"
INVENTORY = ROOT / "docs" / "acceptance" / "map-capability-inventory-047.toml"
PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_47.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-047.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_MAPS_047.md"
API = ROOT / "docs" / "api" / "MAPS.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0074-FIRST-CLASS-MAPS.md"
MAP_SPEC_PLAN = ROOT / "docs" / "acceptance" / "map-spec-plan-047.toml"
MAP_PROVIDER_POLICY = ROOT / "docs" / "acceptance" / "map-provider-policy-047.toml"
MAP_OFFLINE = ROOT / "docs" / "acceptance" / "map-offline-047.toml"
MAP_INTERACTION_COMPAT = ROOT / "docs" / "acceptance" / "map-interaction-compat-047.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
STATUS = ROOT / "STATUS.md"
RELEASE = ROOT / "docs" / "release.toml"
PYPROJECT = ROOT / "pyproject.toml"

TRACKING_ISSUE = "#350"

PACKET_FILES = (
    GATE,
    INVENTORY,
    PACKET,
    UPGRADE,
    IMPLEMENTATION,
    API,
    RFC,
    MAP_SPEC_PLAN,
    MAP_PROVIDER_POLICY,
    MAP_OFFLINE,
    MAP_INTERACTION_COMPAT,
)

EXPECTED_GATES = (
    "SPEC-047",
    "PROVIDER-047",
    "OFFLINE-047",
    "RENDER-047",
    "INTERACT-047",
    "SECURITY-047",
    "A11Y-047",
    "BROWSER-047",
    "PERF-047",
    "ADAPTER-047",
    "TOOLING-047",
    "COMPAT-047",
    "DOCS-047",
    "REGRESS-047",
    "PKG-047",
)
EXPECTED_REQUIREMENT_RANGES = (
    "MAP-SPEC-001..012",
    "MAP-PROVIDER-001..012",
    "MAP-OFFLINE-001..014",
    "MAP-LAYER-001..010",
    "MAP-EVENT-001..010",
    "MAP-ADAPTER-001..006",
)
EXCLUDED_REQUIREMENT_IDS = frozenset({"MAP-ADAPTER-001..006"})

FROZEN_CONTRACT_MARKERS = (
    "hedron.Map",
    "sanitize_geojson",
    "MAP_VIEWPORT_TRIGGER",
    "ActionHandle",
    "MapInteraction",
    "OpenStreetMap.standard",
)


def accepted_contract_present() -> bool:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    return "**Status:** Accepted" in rfc and "| D-078 | Accepted |" in decisions


def contract_refine_present() -> bool:
    decisions = DECISIONS.read_text(encoding="utf-8")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    return "| D-082 | Accepted |" in decisions and all(
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


GATE_TESTS: dict[str, list[str]] = {
    "SPEC-047": ["tests/unit/test_maps_047_spec.py"],
    "PROVIDER-047": ["tests/unit/test_maps_047_provider.py"],
    "OFFLINE-047": ["tests/unit/test_maps_047_offline.py"],
    "RENDER-047": [
        "tests/unit/test_maps_047_render.py",
        "tests/browser/test_maps_047_render.py",
    ],
    "INTERACT-047": ["tests/unit/test_maps_047_interact.py"],
    "SECURITY-047": ["tests/unit/test_maps_047_security.py"],
    "A11Y-047": ["tests/browser/test_maps_047_a11y.py"],
    "BROWSER-047": ["tests/browser/test_maps_047_render.py"],
    "PERF-047": ["tests/unit/test_maps_047_perf.py"],
    "ADAPTER-047": ["tests/unit/test_maps_047_adapter.py"],
    "TOOLING-047": ["tests/unit/test_maps_047_tooling.py"],
    "COMPAT-047": [
        "tests/unit/test_maps_047_compat.py",
        "tests/unit/test_phase15_map.py",
    ],
    "DOCS-047": ["tests/unit/test_maps_047_docs.py"],
    "REGRESS-047": ["tests/unit/test_maps_047_compat.py"],
    "PKG-047": ["tests/unit/test_maps_047_pkg.py"],
}


def run_pytest(paths: list[str]) -> int:
    import subprocess
    import sys

    # Use the active interpreter so `uv run` cannot recreate `.venv` mid-CI
    # (quality already pinned that interpreter).
    command = [sys.executable, "-m", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not accepted_contract_present():
        errors.append("RFC-0074 and D-078 must remain Accepted")
    if not contract_refine_present():
        errors.append("D-082 and the frozen 0.47 contract markers must remain present")
    packet = PACKET.read_text(encoding="utf-8")
    if TRACKING_ISSUE not in packet:
        errors.append(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.47.toml")
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
