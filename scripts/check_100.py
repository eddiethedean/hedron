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
FIXTURE_ROOT = ROOT / "tests/upgrade/phase_1_0"

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
    "docs/acceptance/public-inventory-100.toml",
    "docs/acceptance/stable-inventory-100.toml",
    "docs/acceptance/removal-inventory-100.toml",
    "docs/acceptance/warnings-100.toml",
    "docs/acceptance/baseline-100.json",
    "docs/acceptance/support-policy-100.md",
)

TRANSITIONAL_FIXTURES = {
    "app_component.py": "app.component",
    "app_fragment.py": "app.fragment",
    "app_include_feature.py": "app.include_feature",
    "router_component.py": "router.component",
    "app_screen.py": "app.screen",
    "app_refreshable.py": "app.refreshable",
    "app_command.py": "app.command",
    "app_form_command.py": "app.form_command",
}


def _toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _check_fixture_corpus() -> list[str]:
    """Validate the source fixture shape used by MIGRATE/COMPAT gates."""
    for _source_root in (ROOT / "packages/hedron/src", ROOT / "packages/hedron-core/src"):
        if str(_source_root) not in sys.path:
            sys.path.insert(0, str(_source_root))
    from hedron.migrate.api import scan_api

    errors: list[str] = []
    manifest_path = FIXTURE_ROOT / "manifest.toml"
    if not manifest_path.is_file():
        return ["missing phase-1.0 fixture manifest: tests/upgrade/phase_1_0/manifest.toml"]
    manifest = _toml(manifest_path)
    if manifest.get("schema") != "hedron.upgrade-fixture-manifest/1":
        errors.append("phase-1.0 fixture manifest has an unexpected schema")
    if manifest.get("baseline") != "v0.67.0" or manifest.get("target") != "v1.0.0":
        errors.append("phase-1.0 fixture manifest must span v0.67.0 to v1.0.0")

    canonical = FIXTURE_ROOT / "canonical"
    if not canonical.is_dir():
        errors.append("missing canonical phase-1.0 fixture directory")
    else:
        report = scan_api(canonical)
        if report.findings:
            errors.append("canonical phase-1.0 fixtures contain transitional API findings")

    transitional = FIXTURE_ROOT / "transitional"
    for filename, old_path in TRANSITIONAL_FIXTURES.items():
        path = transitional / filename
        if not path.is_file():
            errors.append(f"missing transitional fixture: {path.relative_to(ROOT)}")
            continue
        findings = scan_api(path).findings
        if not findings or findings[0].old_path != old_path:
            errors.append(f"transitional fixture {filename} does not exercise {old_path}")

    for relative in (
        "negative/undeclared_dynamic.py",
        "negative/invalid_interaction.py",
        "rollback/export.json",
    ):
        if not (FIXTURE_ROOT / relative).is_file():
            errors.append(f"missing phase-1.0 fixture: tests/upgrade/phase_1_0/{relative}")
    return errors


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
    warning_inventory = _toml(ACCEPTANCE / "warnings-100.toml")
    baseline = json.loads((ACCEPTANCE / "baseline-100.json").read_text(encoding="utf-8"))
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
    if warning_inventory.get("baseline") != "v0.67.0":
        errors.append("warning inventory must use the immutable v0.67.0 baseline")
    warning_rows = warning_inventory.get("warning")
    warning_codes = {
        str(row.get("code"))
        for row in warning_rows
        if isinstance(row, dict) and row.get("code")
    } if isinstance(warning_rows, list) else set()
    required_warning_codes = {
        "HED-MIGRATE-0671",
        "HED-MIGRATE-0672",
        "HED-MIGRATE-0673",
        "HED-MIGRATE-0674",
        "HED-MIGRATE-0675",
        "HED-MIGRATE-0676",
        "HED-MIGRATE-0677",
        "HED-MIGRATE-0678",
    }
    if not required_warning_codes <= warning_codes:
        errors.append("warning inventory is missing the implemented warning floor")
    if baseline.get("baseline") != "v0.67.0" or baseline.get("release_cut_satisfied") is not False:
        errors.append("baseline artifact must remain a draft against v0.67.0")

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
    for code in (
        "HED-MIGRATE-0671",
        "HED-MIGRATE-0672",
        "HED-MIGRATE-0673",
        "HED-MIGRATE-0674",
        "HED-MIGRATE-0675",
        "HED-MIGRATE-0676",
        "HED-MIGRATE-0677",
        "HED-MIGRATE-0678",
    ):
        if code not in migration_source:
            errors.append(f"known 0.67 warning floor is missing {code}")

    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for token in ("Stage 0 Refined", "RELEASE_1_0", "release-gate-1.0.toml", "D-117"):
        if token not in roadmap:
            errors.append(f"roadmap does not expose 1.0 packet token {token!r}")

    errors.extend(_check_fixture_corpus())

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
