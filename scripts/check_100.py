#!/usr/bin/env python3
"""Validate the Hedron 1.0 Stage 0 packet without claiming release evidence."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "docs" / "acceptance"
GATE_PATH = ACCEPTANCE / "release-gate-1.0.toml"
CONTRACT_PATH = ACCEPTANCE / "one-zero-cut-contract.toml"
BOM_PATH = ACCEPTANCE / "compatibility-bom-067.toml"
PREDECESSOR_GATE_PATH = ACCEPTANCE / "release-gate-0.67.toml"

EXPECTED_GATES = (
    "ENTRY-100",
    "SURFACE-100",
    "REMOVE-100",
    "MIGRATE-100",
    "COMPAT-100",
    "INTERACTION-100",
    "ENGINE-100",
    "TOOLING-100",
    "TYPE-100",
    "SECURITY-100",
    "A11Y-100",
    "PERF-100",
    "FLEET-100",
    "DOCS-100",
    "REGRESS-100",
    "PKG-100",
    "RELEASE-100",
)

REQUIRED_FILES = (
    "docs/acceptance/RELEASE_1_0.md",
    "docs/acceptance/release-gate-1.0.toml",
    "docs/acceptance/one-zero-cut-contract.toml",
    "docs/acceptance/upgrade-fixtures-1.0.md",
    "docs/acceptance/contract-freeze-067.toml",
    "docs/acceptance/compatibility-bom-067.toml",
    "docs/implementation/HEDRON_1_0.md",
    "docs/rfcs/RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
    "docs/api/HTMX_ALPINE_BOUNDARY_1_0.md",
)


def _toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def check_plan() -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing Stage 0 artifact: {relative}")

    if errors:
        return errors

    gate = _toml(GATE_PATH)
    contract = _toml(CONTRACT_PATH)
    bom = _toml(BOM_PATH)
    predecessor = _toml(PREDECESSOR_GATE_PATH)
    workspace = _toml(ROOT / "pyproject.toml")

    if gate.get("phase") != "1.0" or gate.get("target") != "v1.0.0":
        errors.append("1.0 gate must target v1.0.0")
    if gate.get("status") != "Planned":
        errors.append("Stage 0 must not claim the 1.0 release gate is Verified")
    if gate.get("stage_1_entry_satisfied") is not False:
        errors.append("Stage 1 must remain blocked until ENTRY-100 is Verified")
    if gate.get("release_cut_satisfied") is not False:
        errors.append("Stage 0 must not claim release-cut authorization")

    rows = gate.get("evidence")
    if not isinstance(rows, list):
        errors.append("release gate must contain evidence rows")
        rows = []
    ids = tuple(str(row.get("id")) for row in rows if isinstance(row, dict))
    if ids != EXPECTED_GATES:
        errors.append(f"unexpected 1.0 gate order/content: {ids!r}")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("release gate contains a non-table evidence row")
            continue
        gate_id = str(row.get("id", "<unknown>"))
        if row.get("state") != "Planned":
            errors.append(f"{gate_id}: Stage 0 packet may not pre-verify release evidence")
        if not str(row.get("command", "")).strip():
            errors.append(f"{gate_id}: missing executable command")
        if not str(row.get("owner", "")).strip():
            errors.append(f"{gate_id}: missing owner")

    if contract.get("status") != "Stage 0 Refined; implementation and release evidence pending":
        errors.append("cut contract must state the refined-but-unimplemented status exactly")
    if contract.get("planning_baseline") != "v0.67.0":
        errors.append("cut contract must use immutable v0.67.0 as its baseline")
    if (
        contract.get("changes_runtime") is not False
        or contract.get("changes_versions") is not False
    ):
        errors.append("Stage 0 refinement cannot change runtime or package versions")
    if contract.get("stage_1_entry_satisfied") is not False:
        errors.append("cut contract must retain the W0/ENTRY-100 blocker")

    release_boundary = contract.get("release_boundary")
    if not isinstance(release_boundary, dict):
        errors.append("cut contract lacks [release_boundary]")
    elif release_boundary.get("net_new_required_runtime_capabilities") != 0:
        errors.append("1.0 may not add a net-new Required runtime capability")

    migration = contract.get("migration")
    if not isinstance(migration, dict):
        errors.append("cut contract lacks [migration]")
    else:
        for token in (
            "HedronFutureWarning",
            "hedron check --target 1.0",
            "hedron migrate api --target 1.0",
        ):
            if token not in " ".join(str(value) for value in migration.values()):
                errors.append(f"migration contract omits {token!r}")

    if predecessor.get("status") != "Verified" or predecessor.get("target") != "v0.67.0":
        errors.append("1.0 requires the Verified v0.67.0 predecessor gate")
    if bom.get("status") != "Verified for the v0.67.0 bridge; 1.0 execution pending":
        errors.append(
            "compatibility BOM status must distinguish the Verified bridge from pending 1.0"
        )
    if "1.0 canonical" not in str(bom.get("source_compatibility", "")):
        errors.append("compatibility BOM must retain the 1.0-on-0.67 source promise")

    project = workspace.get("project")
    current_version = project.get("version") if isinstance(project, dict) else None
    if current_version != "0.67.0":
        errors.append(
            f"Stage 0 refinement must leave workspace at 0.67.0, found {current_version!r}"
        )

    migration_source = (ROOT / "packages/hedron-core/src/hedron_core/migration.py").read_text(
        encoding="utf-8"
    )
    for code in ("HED-MIGRATE-0671", "HED-MIGRATE-0672", "HED-MIGRATE-0673"):
        if code not in migration_source:
            errors.append(f"known 0.67 warning floor is missing {code}")

    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for token in ("Stage 0 Refined", "RELEASE_1_0", "release-gate-1.0.toml", "D-117"):
        if token not in roadmap:
            errors.append(f"roadmap does not expose 1.0 packet token {token!r}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-plan", action="store_true", help="validate the Stage 0 packet")
    parser.add_argument("--gate", choices=EXPECTED_GATES, help="select one release gate")
    parser.add_argument("--verify", action="store_true", help="require selected release evidence")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    errors = check_plan()
    if args.gate and args.verify and not errors:
        errors.append(
            f"{args.gate} is Planned: Stage 0 defines the gate but does not provide "
            "implementation evidence"
        )

    payload = {
        "schema": "hedron.phase-1.0-plan-check/1",
        "ok": not errors,
        "mode": "release-verify" if args.verify else "stage-0-plan",
        "gate": args.gate,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        print("Hedron 1.0 Stage 0 packet: OK (release gates remain Planned)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
