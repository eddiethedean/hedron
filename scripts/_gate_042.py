#!/usr/bin/env python3
"""Shared helpers for phase 0.42 production-grade Web Component platform gates."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.42.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_42.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_ELEMENTS_042.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0060-WEB-COMPONENT-PLATFORM.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-042" / "BRIEF.md"
UPGRADE = ROOT / "docs" / "acceptance" / "upgrade-fixtures-042.md"
INVENTORY = ROOT / "docs" / "acceptance" / "supported-element-inventory-042.toml"
FLEET_INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-042.toml"
AT_PROTOCOL = ROOT / "docs" / "acceptance" / "human-at" / "042" / "PROTOCOL.md"
AT_DISPOSITION = ROOT / "docs" / "acceptance" / "human-at" / "042" / "DISPOSITION.toml"
DECISIONS = ROOT / "docs" / "DECISIONS.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
RELEASE_TOML = ROOT / "docs" / "release.toml"

EXPECTED_GATES = (
    "STABLE-042",
    "COMPAT-042",
    "REVIEW-042",
    "AT-042",
    "PERF-042",
    "SUPPLY-042",
    "REGRESS-042",
    "PKG-042",
)

TRACKING_ISSUE = "#97"
MEDIUM_ISSUES = (
    99,
    100,
    108,
    136,
    137,
    138,
    139,
    140,
    141,
    145,
    146,
    147,
    148,
    151,
    152,
    156,
    160,
    174,
    175,
    177,
    187,
    205,
    206,
    208,
    217,
    218,
    238,
    242,
    243,
    245,
    246,
    249,
)

PACKET_FILES = (
    RELEASE_PACKET,
    GATE,
    IMPLEMENTATION,
    RFC,
    REVIEW_BRIEF,
    UPGRADE,
    INVENTORY,
    FLEET_INVENTORY,
    AT_PROTOCOL,
    AT_DISPOSITION,
    DECISIONS,
)

# Domain evidence. Packet integrity lives only under PKG-042 (not padded into every gate).
GATE_TESTS: dict[str, list[str]] = {
    "STABLE-042": [
        "tests/unit/test_stable_042.py",
    ],
    "COMPAT-042": [
        "tests/unit/test_compat_042.py",
        "tests/browser/test_browser_matrix.py",
        "tests/browser/test_htmx_lifecycle.py",
    ],
    "REVIEW-042": [
        "tests/unit/test_review_042.py",
        "tests/unit/test_phase20_production_gates.py",
    ],
    "AT-042": [
        "tests/unit/test_at_042.py",
    ],
    "PERF-042": [
        "tests/unit/test_perf_042.py",
        "tests/performance/test_budgets.py",
    ],
    "SUPPLY-042": [
        "tests/unit/test_supply_042.py",
    ],
    "REGRESS-042": [
        "tests/unit/test_regress_042_issues.py",
        "tests/unit/test_cache_single_flight_async.py",
        "tests/unit/test_phase05_platform.py::test_cache_data_caches_none_results",
        "tests/unit/test_snowflake_source.py::test_assert_select_only_allows_semicolon_inside_literals",
        "tests/integration/test_workbench_runner.py::test_prepare_app_exports_into_caller_environ",
        "tests/adapters/workbench/test_cli.py::test_check_discover_binds_before_rserver_url",
        "tests/unit/test_phase15_identity.py::test_login_csrf_accepts_valid_cookie_when_session_diverges",
        "tests/unit/test_phase15_identity.py::test_auth_rate_limiter_evicts_stale_ip_keys",
        "tests/unit/test_models_security.py::test_secret_hash_handles_unhashable_inner_value",
    ],
    "PKG-042": ["tests/unit/test_phase042_packet.py"],
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


def rfc_is_accepted() -> bool:
    return RFC.is_file() and "**Status:** Accepted" in RFC.read_text(encoding="utf-8")[:800]


def rfc_resolved_questions_present() -> bool:
    return RFC.is_file() and "Resolved questions (D-070)" in RFC.read_text(encoding="utf-8")


def d070_present() -> bool:
    return DECISIONS.is_file() and "| D-070 | Accepted |" in DECISIONS.read_text(encoding="utf-8")


def medium_issue_refs() -> tuple[str, ...]:
    return tuple(f"#{n}" for n in MEDIUM_ISSUES)


def missing_refine_citations() -> list[str]:
    errors: list[str] = []
    required = (RELEASE_PACKET, DECISIONS, ROADMAP, RFC)
    refs = (TRACKING_ISSUE, *medium_issue_refs())
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [ref for ref in refs if ref not in text]
        if missing:
            errors.append(f"{path}: missing 0.42 issue refs {missing}")
    if RFC.is_file() and not rfc_resolved_questions_present():
        errors.append("RFC-0060 must include 'Resolved questions (D-070)'")
    if DECISIONS.is_file():
        decisions = DECISIONS.read_text(encoding="utf-8")
        if "v0.41.0" not in decisions.split("| D-070 |", 1)[-1][:3500]:
            errors.append("D-070 must baseline Published v0.41.0")
    return errors


def living_published_baseline() -> str:
    data = tomllib.loads(RELEASE_TOML.read_text(encoding="utf-8"))
    release = data.get("release") or {}
    return f"v{str(release.get('published_version', '')).strip()}"


def run_pytest(paths: list[str]) -> int:
    command = ["uv", "run", "pytest", "-q", "--tb=short", *paths]
    print("+", *command, flush=True)
    return subprocess.call(command, cwd=ROOT)


def check_gate(gate_id: str) -> int:
    errors: list[str] = []
    require_files(list(PACKET_FILES), errors)
    if not rfc_is_accepted():
        errors.append("RFC-0060 must be Accepted")
    if not d070_present():
        errors.append("D-070 must be Accepted in DECISIONS.md")
    if not rfc_resolved_questions_present():
        errors.append("RFC-0060 must include Resolved questions (D-070)")
    state = gate_state(gate_id)
    if state is None:
        errors.append(f"{gate_id} missing from release-gate-0.42.toml")
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
