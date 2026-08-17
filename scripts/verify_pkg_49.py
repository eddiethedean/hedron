#!/usr/bin/env python3
"""Verify the phase 0.49 FastAPI/Pydantic convergence Stage 0 packet.

This command never publishes, tags, or implements 0.49 runtime. Use
``--allow-planned`` while every 0.49 gate is Planned and the living baseline is
0.48.0. Omitting the flag requires a 0.49 cut that this refine does not make.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

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
PREDECESSOR = "0.48.0"
RELEASE_CANDIDATE = "0.49.0"

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


def _load(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_packet_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PACKET_FILES if not path.is_file()]
    if missing:
        raise SystemExit(f"missing 0.49 packet files: {missing}")
    print("ok: 0.49 contract packet files")


def _check_gates(*, allow_planned: bool) -> None:
    rows = _load(GATE).get("evidence")
    if not isinstance(rows, list):
        raise SystemExit(f"{GATE}: [[evidence]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in rows if isinstance(row, dict))
    if found != EXPECTED_GATES:
        raise SystemExit(f"{GATE}: expected {EXPECTED_GATES}; found {found}")
    if str(_load(GATE).get("planning_baseline", "")).strip() != f"v{PREDECESSOR}":
        raise SystemExit(f"{GATE}: planning_baseline must be v{PREDECESSOR}")
    if str(_load(GATE).get("contract_refine", "")).strip() != "D-084":
        raise SystemExit(f"{GATE}: contract_refine must be D-084")
    if allow_planned:
        non_planned = [
            f"{row.get('id')}={row.get('state')}"
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Planned"
        ]
        if non_planned:
            raise SystemExit(f"Stage 0 requires Planned gates: {non_planned}")
    else:
        non_verified = [
            f"{row.get('id')}={row.get('state')}"
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Verified"
        ]
        if non_verified:
            raise SystemExit(f"cut requires Verified gates: {non_verified}")
    print("ok: release-gate-0.49.toml exact gate inventory")


def _check_inventory(*, allow_planned: bool) -> None:
    data = _load(INVENTORY)
    required = {
        "phase": "0.49",
        "planning_baseline": f"v{PREDECESSOR}",
        "required_predecessor": f"v{PREDECESSOR}",
        "target": f"v{RELEASE_CANDIDATE}",
        "decision": "D-081",
        "contract_refine": "D-084",
        "owning_rfc": "RFC-0076",
        "lifetime_lock": "docs/acceptance/fastapi-lifetime-049.toml",
        "binding_lock": "docs/acceptance/fastapi-binding-049.toml",
        "typeschema_v2_lock": "docs/acceptance/typeschema-v2-049.toml",
        "unions_openapi_lock": "docs/acceptance/fastapi-unions-openapi-049.toml",
        "settings_research_lock": "docs/acceptance/fastapi-settings-research-049.toml",
        "tracking": TRACKING_ISSUE,
    }
    for key, expected in required.items():
        if str(data.get(key, "")).strip() != expected:
            raise SystemExit(f"{INVENTORY}: {key} must be {expected!r}")
    capabilities = data.get("capability")
    if not isinstance(capabilities, list):
        raise SystemExit(f"{INVENTORY}: [[capability]] rows required")
    found = tuple(str(row.get("id", "")).strip() for row in capabilities if isinstance(row, dict))
    if found != EXPECTED_REQUIREMENT_RANGES:
        raise SystemExit(
            f"{INVENTORY}: requirement coverage drift; expected "
            f"{EXPECTED_REQUIREMENT_RANGES}; found {found}"
        )
    adapter = next(
        (
            row
            for row in capabilities
            if isinstance(row, dict) and row.get("id") == "FP-ADAPTER-001..008"
        ),
        None,
    )
    if adapter is None:
        raise SystemExit(f"{INVENTORY}: FP-ADAPTER-001..008 missing")
    adopt = adapter.get("adopt_if_measured")
    if not isinstance(adopt, list) or "fail-fast-batch" in {str(item) for item in adopt}:
        raise SystemExit(f"{INVENTORY}: FailFast must not appear on FP-ADAPTER adopt_if_measured")
    expected_status = "Planned" if allow_planned else "Verified"
    if str(data.get("status", "")).strip() != expected_status:
        raise SystemExit(f"{INVENTORY}: status must be {expected_status!r}")
    bad_states: list[str] = []
    for row in capabilities:
        if not isinstance(row, dict):
            continue
        requirement_id = str(row.get("id", "")).strip()
        state = str(row.get("state", "")).strip()
        if requirement_id in EXCLUDED_REQUIREMENT_IDS:
            if state != "Excluded":
                bad_states.append(requirement_id)
            continue
        if requirement_id in EVALUATE_REQUIREMENT_IDS:
            if state != "Evaluate":
                bad_states.append(requirement_id)
            continue
        if requirement_id in EXPERIMENTAL_REQUIREMENT_IDS:
            if state != "Experimental":
                bad_states.append(requirement_id)
            continue
        if state != expected_status:
            bad_states.append(requirement_id)
    if bad_states:
        raise SystemExit(f"{INVENTORY}: expected states missing for {bad_states}")
    print("ok: fastapi-pydantic-capability-inventory-049.toml complete requirement coverage")


def _check_contract() -> None:
    rfc = RFC.read_text(encoding="utf-8")
    decisions = DECISIONS.read_text(encoding="utf-8")
    if "**Status:** Accepted" not in rfc or "| D-081 | Accepted |" not in decisions:
        raise SystemExit("RFC-0076 and D-081 must remain Accepted")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (RFC, IMPLEMENTATION, API, PACKET)
    )
    if "| D-084 | Accepted |" not in decisions or not all(
        marker in combined for marker in FROZEN_CONTRACT_MARKERS
    ):
        raise SystemExit("D-084 and the frozen 0.49 contract markers must remain present")
    if TRACKING_ISSUE not in PACKET.read_text(encoding="utf-8"):
        raise SystemExit(f"{PACKET}: tracking issue {TRACKING_ISSUE} must be bound")
    if TRACKING_ISSUE not in rfc:
        raise SystemExit(f"{RFC}: tracking issue {TRACKING_ISSUE} must be bound")
    for path in (ROADMAP, STATUS, API, IMPLEMENTATION):
        text = path.read_text(encoding="utf-8")
        for marker in ("0.48", "0.49", "D-081", "D-084"):
            if marker not in text:
                raise SystemExit(f"{path}: missing 0.49 traceability marker {marker}")
    print("ok: RFC-0076 / D-081 / D-084 boundary and traceability")


def _check_versions(*, allow_planned: bool) -> None:
    workspace = str(_load(PYPROJECT).get("project", {}).get("version", "")).strip()
    release = _load(RELEASE).get("release", {})
    if not isinstance(release, dict):
        raise SystemExit(f"{RELEASE}: [release] table required")
    published = str(release.get("published_version", "")).strip()
    development = str(release.get("development_version", "")).strip()
    if allow_planned:
        if published != PREDECESSOR:
            raise SystemExit(f"published baseline must remain {PREDECESSOR}; found {published!r}")
        if workspace != PREDECESSOR or development != PREDECESSOR:
            raise SystemExit(
                f"workspace/development version must stay {PREDECESSOR}; "
                f"found {workspace}/{development}"
            )
    elif published.startswith("0.50."):
        print(f"ok: 0.49 historical under living published {published}")
        return
    else:
        if published != RELEASE_CANDIDATE:
            raise SystemExit(
                f"cut published version must be {RELEASE_CANDIDATE}; found {published!r}"
            )
        if workspace != RELEASE_CANDIDATE or development != RELEASE_CANDIDATE:
            raise SystemExit(
                f"workspace/development version must be {RELEASE_CANDIDATE}; "
                f"found {workspace}/{development}"
            )
    print(f"ok: version honesty (published {published}, development {development})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-planned", action="store_true")
    args = parser.parse_args(argv)
    _check_packet_files()
    _check_gates(allow_planned=args.allow_planned)
    _check_inventory(allow_planned=args.allow_planned)
    _check_contract()
    _check_versions(allow_planned=args.allow_planned)

    import check_release_gate as release_gate

    if args.allow_planned:
        errors = release_gate.check_evidence_manifest_lenient(GATE)
        if errors:
            raise SystemExit("\n".join(errors))
        print("ok: 0.49 planned gate shape")
    else:
        raise SystemExit(
            "0.49 is Stage 0 only; omit --allow-planned only after an in-tree v0.49.0 cut"
        )
    print(f"ok: verify_pkg_49 ({'allow-planned' if args.allow_planned else 'cut'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
