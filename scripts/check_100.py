#!/usr/bin/env python3
"""Validate the Hedron 1.0 Stage 0 packet without claiming release evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tomllib
from pathlib import Path

from hedron_core.migration import PUBLIC_FUTURE_WARNINGS

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "docs" / "acceptance"
GATE_PATH = ACCEPTANCE / "release-gate-1.0.toml"
CONTRACT_PATH = ACCEPTANCE / "one-zero-cut-contract.toml"
BOM_PATH = ACCEPTANCE / "compatibility-bom-067.toml"
PREDECESSOR_GATE_PATH = ACCEPTANCE / "release-gate-0.67.toml"
FIXTURE_ROOT = ROOT / "tests/upgrade/phase_1_0"
MAINTAINED_CONSUMERS = (
    "examples/connect-reference",
    "examples/fastapi-pydantic",
    "examples/file-upload",
    "examples/live-interaction",
    "examples/notes-sqlalchemy",
    "examples/oidc",
    "examples/package-workflows",
    "examples/reference-app",
    "examples/session-auth",
    "examples/workbench-reference",
    "packages/hedron/README.md",
)

# These are first-party authoring surfaces rather than historical migration
# records.  Keep them on the same one-clear-way lint as runnable examples so a
# future docs edit cannot quietly reintroduce a removed 0.x spelling.
MAINTAINED_DOC_ROOTS = (
    "docs/components",
    "docs/demos/runnable",
    "docs/examples",
    "docs/guides",
)
MAINTAINED_DOC_EXCLUDES = frozenset(
    {
        "docs/guides/upgrade.md",
        "docs/guides/whats-new-0.43.md",
        "docs/guides/whats-new-0.46.md",
    }
)

COORDINATED_PACKAGES = (
    "hedron-core",
    "hedron",
    "hedron-explorer",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-conformance",
    "hedron-extras",
    "hedron-workbench",
    "hedron-posit",
    "hedron-elements",
)

INDEPENDENT_SATELLITES = (
    "hedron-charts",
    "hedron-maps",
    "hedron-native",
    "hedron-mcp",
    "hedron-gradio",
    "hedron-sample-kit",
    "hedron-notebook",
    "hedron-sim",
    "fastapi-workbench",
    "edron",
)

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
    "docs/acceptance/task-inventory-100.toml",
    "docs/acceptance/removal-inventory-100.toml",
    "docs/acceptance/warnings-100.toml",
    "docs/acceptance/baseline-100.json",
    "docs/acceptance/support-policy-100.md",
    "docs/acceptance/compatibility-report-100/README.md",
    "docs/acceptance/compatibility-report-100/local-bridge.json",
    "scripts/generate_100_inventory.py",
    "scripts/check_upgrade_100.py",
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
    "flask_component.py": "flask.component",
    "blueprint_component.py": "blueprint.component",
    "blueprint_include_feature.py": "blueprint.include_feature",
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


def _check_package_metadata() -> list[str]:
    """Ensure the v1.0 coordinated train cannot drift from package metadata."""
    errors: list[str] = []
    try:
        workspace = _toml(ROOT / "pyproject.toml").get("project", {})
    except (OSError, ValueError):
        return ["unable to read root package metadata"]
    if not isinstance(workspace, dict) or workspace.get("version") != "1.0.0":
        errors.append("root workspace metadata must declare version 1.0.0")

    for distribution in COORDINATED_PACKAGES:
        package_dir = ROOT / "packages" / distribution
        pyproject = package_dir / "pyproject.toml"
        if not pyproject.is_file():
            errors.append(f"missing coordinated package metadata: {distribution}")
            continue
        project = _toml(pyproject).get("project", {})
        if not isinstance(project, dict) or project.get("version") != "1.0.0":
            errors.append(f"{distribution}: coordinated package must declare version 1.0.0")
            continue
        module = distribution.replace("-", "_")
        init = package_dir / "src" / module / "__init__.py"
        if not init.is_file():
            errors.append(f"{distribution}: missing package __init__")
        elif '__version__ = "1.0.0"' not in init.read_text(encoding="utf-8"):
            errors.append(f"{distribution}: __version__ is not 1.0.0")

    for distribution in INDEPENDENT_SATELLITES:
        pyproject = ROOT / "packages" / distribution / "pyproject.toml"
        if not pyproject.is_file():
            errors.append(f"missing independent satellite metadata: {distribution}")
            continue
        project = _toml(pyproject).get("project", {})
        dependencies = project.get("dependencies", []) if isinstance(project, dict) else []
        joined = " ".join(str(item) for item in dependencies)
        if (
            distribution != "hedron-native"
            and "hedron" in joined
            and (">=0.67" not in joined or "<2.0" not in joined)
        ):
            errors.append(f"{distribution}: Hedron dependency must explicitly span 0.67 and 1.x")
        module = distribution.replace("-", "_")
        init = ROOT / "packages" / distribution / "src" / module / "__init__.py"
        if not init.is_file():
            errors.append(f"{distribution}: missing package __init__")
    return errors


def _check_maintained_consumers() -> list[str]:
    """Keep first-party maintained examples on the one-clear-way surface."""
    for _source_root in (ROOT / "packages/hedron/src", ROOT / "packages/hedron-core/src"):
        if str(_source_root) not in sys.path:
            sys.path.insert(0, str(_source_root))
    from hedron.migrate.api import scan_api

    errors: list[str] = []
    for relative in MAINTAINED_CONSUMERS:
        path = ROOT / relative
        if not path.exists():
            errors.append(f"missing maintained consumer: {relative}")
            continue
        findings = scan_api(path).findings
        if findings:
            details = ", ".join(f"{item.old_path}@{item.line}" for item in findings[:3])
            suffix = "..." if len(findings) > 3 else ""
            errors.append(
                f"maintained consumer contains transitional API ({relative}): {details}{suffix}"
            )
    for relative_root in MAINTAINED_DOC_ROOTS:
        root = ROOT / relative_root
        if not root.is_dir():
            errors.append(f"missing maintained docs root: {relative_root}")
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".py"}:
                continue
            relative = path.relative_to(ROOT).as_posix()
            if relative in MAINTAINED_DOC_EXCLUDES:
                continue
            findings = scan_api(path).findings
            if findings:
                details = ", ".join(f"{item.old_path}@{item.line}" for item in findings[:3])
                suffix = "..." if len(findings) > 3 else ""
                errors.append(
                    f"maintained docs contain transitional API ({relative}): {details}{suffix}"
                )
    return errors


def _check_inventory_classification(
    public_inventory: dict[str, object], stable_inventory: dict[str, object]
) -> list[str]:
    """Ensure generated W0 inventories have no silent/unknown rows.

    The generator is intentionally conservative: non-root package exports are
    package-native and repository artifacts are supporting material, not
    automatically SemVer-stable.  This check protects that distinction and
    verifies that the stable export enumeration covers the public export set.
    """
    errors: list[str] = []
    allowed_maturity = {"stable", "beta", "experimental", "internal"}
    allowed_dispositions = {
        "stable",
        "beta",
        "experimental",
        "package-native",
        "coordinated-cut",
        "independent-satellite",
        "package-metadata",
        "documentation",
        "maintained-example",
        "verification",
        "tooling",
        "ci",
        "repository-support",
    }
    public_rows = public_inventory.get("surface")
    public_artifacts = public_inventory.get("artifact")
    stable_rows = stable_inventory.get("symbol")
    if not isinstance(public_rows, list) or not isinstance(stable_rows, list):
        return ["W0 inventories must contain [[surface]] and [[symbol]] rows"]
    public_symbols: set[str] = set()
    for row in public_rows:
        if not isinstance(row, dict):
            errors.append("public inventory contains a non-table surface row")
            continue
        canonical = str(row.get("canonical", ""))
        if not canonical:
            errors.append("public inventory surface is missing canonical identity")
        else:
            public_symbols.add(canonical)
        if not str(row.get("owner", "")).strip():
            errors.append(f"public inventory {canonical or '<unknown>'} is missing owner")
        maturity = str(row.get("maturity", ""))
        disposition = str(row.get("disposition", ""))
        if maturity not in allowed_maturity:
            errors.append(f"public inventory {canonical or '<unknown>'} has unknown maturity")
        if disposition not in allowed_dispositions:
            errors.append(f"public inventory {canonical or '<unknown>'} has unknown disposition")
    if isinstance(public_artifacts, list):
        for row in public_artifacts:
            if not isinstance(row, dict):
                errors.append("public inventory contains a non-table artifact row")
                continue
            identity = str(row.get("path", "<unknown>"))
            for field in ("task", "owner", "maturity", "disposition"):
                if not str(row.get(field, "")).strip():
                    errors.append(f"public inventory artifact {identity} is missing {field}")
            if str(row.get("maturity", "")) not in allowed_maturity:
                errors.append(f"public inventory artifact {identity} has unknown maturity")
            if str(row.get("disposition", "")) not in allowed_dispositions:
                errors.append(f"public inventory artifact {identity} has unknown disposition")
    else:
        errors.append("public inventory must contain artifact rows")
    stable_symbols: set[str] = set()
    for row in stable_rows:
        if not isinstance(row, dict):
            errors.append("stable inventory contains a non-table symbol row")
            continue
        qualified = str(row.get("qualified", ""))
        if not qualified:
            errors.append("stable inventory symbol is missing qualified identity")
        else:
            stable_symbols.add(qualified)
        if str(row.get("maturity", "")) != "stable":
            errors.append(f"stable inventory {qualified or '<unknown>'} is not stable")
        if str(row.get("disposition", "")) != "stable":
            errors.append(f"stable inventory {qualified or '<unknown>'} has non-stable disposition")
    expected_stable = {
        str(row.get("canonical"))
        for row in public_rows
        if isinstance(row, dict) and str(row.get("maturity", "")) == "stable"
    }
    if stable_symbols != expected_stable:
        missing = sorted(expected_stable - stable_symbols)
        extra = sorted(stable_symbols - expected_stable)
        if missing:
            errors.append(f"stable inventory omits stable public exports: {missing[:3]!r}")
        if extra:
            errors.append(f"stable inventory has non-stable exports: {extra[:3]!r}")
    return errors


def _check_task_inventory(task_inventory: dict[str, object], baseline_commit: str) -> list[str]:
    """Validate the AST-derived task/interface graph and its provenance."""
    errors: list[str] = []
    if task_inventory.get("baseline") != "v0.67.0":
        errors.append("task inventory must use immutable v0.67.0")
    if task_inventory.get("baseline_commit") != baseline_commit:
        errors.append("task inventory baseline commit differs from baseline artifact")
    rows = task_inventory.get("task")
    if not isinstance(rows, list) or not rows:
        return ["task inventory must enumerate public classes, functions, and methods"]
    identities: set[str] = set()
    interfaces: set[str] = set()
    allowed_kinds = {"class", "function", "method"}
    allowed_maturity = {"stable", "beta", "experimental", "internal"}
    for row in rows:
        if not isinstance(row, dict):
            errors.append("task inventory contains a non-table row")
            continue
        task = str(row.get("task", ""))
        interface = str(row.get("interface", ""))
        if not task or not interface:
            errors.append("task inventory rows require task and interface identities")
            continue
        if task in identities:
            errors.append(f"task inventory contains duplicate task {task}")
        identities.add(task)
        if interface in interfaces and str(row.get("kind")) != "method":
            errors.append(f"task inventory contains duplicate interface {interface}")
        interfaces.add(interface)
        if str(row.get("kind", "")) not in allowed_kinds:
            errors.append(f"task inventory {task} has unknown kind")
        if not str(row.get("source", "")).strip() or not str(row.get("owner", "")).strip():
            errors.append(f"task inventory {task} is missing source or owner")
        if str(row.get("maturity", "")) not in allowed_maturity:
            errors.append(f"task inventory {task} has unknown maturity")
        if str(row.get("disposition", "")) != "package-native":
            errors.append(f"task inventory {task} must retain package-native ownership")
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
    removal_inventory = _toml(ACCEPTANCE / "removal-inventory-100.toml")
    public_inventory = _toml(ACCEPTANCE / "public-inventory-100.toml")
    stable_inventory = _toml(ACCEPTANCE / "stable-inventory-100.toml")
    task_inventory = _toml(ACCEPTANCE / "task-inventory-100.toml")
    baseline = json.loads((ACCEPTANCE / "baseline-100.json").read_text(encoding="utf-8"))
    compatibility = json.loads(
        (ACCEPTANCE / "compatibility-report-100/local-bridge.json").read_text(encoding="utf-8")
    )
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

    if contract.get("status") != "Implementation in progress; release evidence pending":
        errors.append("cut contract must state the implementation-in-progress status exactly")
    if contract.get("planning_baseline") != "v0.67.0":
        errors.append("cut contract must use immutable v0.67.0 as its baseline")
    if contract.get("changes_runtime") is not False or contract.get("changes_versions") is not True:
        errors.append(
            "1.0 implementation must keep runtime corrections explicit and version metadata bumped"
        )
    if contract.get("stage_1_entry_satisfied") is not False:
        errors.append("cut contract must retain the W0/ENTRY-100 blocker")
    if warning_inventory.get("baseline") != "v0.67.0":
        errors.append("warning inventory must use the immutable v0.67.0 baseline")
    warning_rows = warning_inventory.get("warning")
    warning_codes = (
        {str(row.get("code")) for row in warning_rows if isinstance(row, dict) and row.get("code")}
        if isinstance(warning_rows, list)
        else set()
    )
    required_warning_codes = {
        "HED-MIGRATE-0671",
        "HED-MIGRATE-0672",
        "HED-MIGRATE-0673",
        "HED-MIGRATE-0674",
        "HED-MIGRATE-0675",
        "HED-MIGRATE-0676",
        "HED-MIGRATE-0677",
        "HED-MIGRATE-0678",
        "HED-MIGRATE-0679",
        "HED-MIGRATE-0680",
        "HED-MIGRATE-0681",
    }
    if not required_warning_codes <= warning_codes:
        errors.append("warning inventory is missing the implemented warning floor")
    registry_issues = PUBLIC_FUTURE_WARNINGS.validate(root=ROOT)
    errors.extend(f"warning registry: {issue}" for issue in registry_issues)
    removal_rows = removal_inventory.get("removal")
    removal_codes = (
        {str(row.get("code")) for row in removal_rows if isinstance(row, dict) and row.get("code")}
        if isinstance(removal_rows, list)
        else set()
    )
    if removal_codes != required_warning_codes:
        errors.append("removal inventory must contain exactly one row for each warning code")
    if baseline.get("baseline") != "v0.67.0" or baseline.get("release_cut_satisfied") is not False:
        errors.append("baseline artifact must remain a draft against v0.67.0")
    baseline_commit = baseline.get("baseline_commit")
    if not isinstance(baseline_commit, str) or len(baseline_commit) != 40:
        errors.append("baseline artifact must record the immutable v0.67.0 commit")
    source_digest = baseline.get("source_digest")
    if (
        not isinstance(source_digest, str)
        or len(source_digest) != hashlib.sha256().digest_size * 2
        or any(char not in "0123456789abcdef" for char in source_digest)
    ):
        errors.append("baseline artifact must record a SHA-256 digest of tracked baseline files")
    generation = baseline.get("generation")
    if (
        not isinstance(generation, dict)
        or generation.get("tracked_file_digest") != "sha256(path + bytes, sorted)"
    ):
        errors.append("baseline artifact must identify the all-tracked-file digest algorithm")
    for name, inventory, minimum in (
        ("public", public_inventory, 1),
        ("stable", stable_inventory, 1),
    ):
        if inventory.get("baseline") != "v0.67.0":
            errors.append(f"{name} inventory must use immutable v0.67.0")
        if inventory.get("baseline_commit") != baseline_commit:
            errors.append(f"{name} inventory baseline commit differs from baseline artifact")
        rows = inventory.get("surface" if name == "public" else "symbol")
        if not isinstance(rows, list) or len(rows) < minimum:
            errors.append(f"{name} inventory must enumerate exported/artifact rows")
    counts = baseline.get("inventory_counts")
    if not isinstance(counts, dict):
        errors.append("baseline artifact must retain generated inventory counts")
    elif not isinstance(counts.get("public"), dict) or not isinstance(counts.get("stable"), dict):
        errors.append("baseline inventory counts must contain public and stable sections")
    if isinstance(baseline_commit, str) and len(baseline_commit) == 40:
        try:
            expected_commit = subprocess.check_output(
                ["git", "rev-list", "-1", "v0.67.0"],
                cwd=ROOT,
                text=True,
                stderr=subprocess.STDOUT,
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            errors.append("immutable v0.67.0 git tag is unavailable")
        else:
            if expected_commit != baseline_commit:
                errors.append("baseline artifact does not match the v0.67.0 git tag")
    if isinstance(baseline_commit, str):
        errors.extend(_check_task_inventory(task_inventory, baseline_commit))
    if (
        compatibility.get("schema") != "hedron.compatibility-report/1"
        or compatibility.get("baseline") != "v0.67.0"
        or compatibility.get("target") != "v1.0.0"
        or compatibility.get("status") != "blocked"
        or compatibility.get("release_claim") is not False
    ):
        errors.append("compatibility report must remain an honest blocked draft")
    target_artifact = compatibility.get("target_artifact")
    if not isinstance(target_artifact, dict) or target_artifact.get("available") is not False:
        errors.append("compatibility report may not claim a v1.0.0 artifact is available")
    bridge_run = compatibility.get("bridge_run")
    if not isinstance(bridge_run, dict):
        errors.append("compatibility report must retain the executable baseline bridge run")
    else:
        if bridge_run.get("baseline_commit") != baseline_commit:
            errors.append("compatibility bridge run must use the recorded immutable baseline")
        facts = bridge_run.get("facts")
        if not isinstance(facts, dict) or facts.get("http_status") != 200:
            errors.append("compatibility bridge run must record a successful canonical HTTP probe")

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
    if current_version != "1.0.0":
        errors.append(f"v1.0 branch must set workspace version to 1.0.0, found {current_version!r}")

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
        "HED-MIGRATE-0679",
        "HED-MIGRATE-0680",
        "HED-MIGRATE-0681",
    ):
        if code not in migration_source:
            errors.append(f"known 0.67 warning floor is missing {code}")

    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for token in ("Stage 0 Refined", "RELEASE_1_0", "release-gate-1.0.toml", "D-117"):
        if token not in roadmap:
            errors.append(f"roadmap does not expose 1.0 packet token {token!r}")

    errors.extend(_check_fixture_corpus())
    errors.extend(_check_package_metadata())
    errors.extend(_check_maintained_consumers())
    errors.extend(_check_inventory_classification(public_inventory, stable_inventory))

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
