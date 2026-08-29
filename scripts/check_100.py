#!/usr/bin/env python3
"""Validate the Hedron 1.0 packet and execute available release-gate evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "docs" / "acceptance"

# Keep the documented ``python scripts/check_100.py`` invocation usable from a
# clean source checkout.  The checker is a Stage-0 repository tool and must not
# require an editable install merely to validate the packet.  Insert the source
# roots before importing runtime metadata so the checker validates the same
# source tree it is checking rather than an unrelated installed version.
for _source_root in (
    ROOT / "packages" / "hedron-core" / "src",
    ROOT / "packages" / "hedron" / "src",
):
    if _source_root.is_dir() and str(_source_root) not in sys.path:
        sys.path.insert(0, str(_source_root))

from hedron_core.migration import PUBLIC_FUTURE_WARNINGS  # noqa: E402

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
    "edron-sim",
    "fastapi-workbench",
    "edron",
)

PLUGIN_DEFINITION_SATELLITES = frozenset(
    {
        "hedron-charts",
        "hedron-gradio",
        "hedron-maps",
        "hedron-mcp",
        "hedron-notebook",
        "hedron-sample-kit",
    }
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
    "docs/acceptance/compatibility-report-100/local-build-evidence.json",
    "docs/acceptance/compatibility-report-100/verification-100.json",
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


def _run(command: list[str], *, extra_env: dict[str, str] | None = None) -> list[str]:
    """Run one repository evidence command and return concise findings."""
    runner = ROOT / ".venv" / "bin" / "python"
    executable = str(runner) if runner.is_file() else sys.executable
    resolved = [executable, *command[1:]] if command and command[0] == sys.executable else command
    source_roots = sorted(ROOT.glob("packages/*/src"))
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(str(path) for path in source_roots),
        **(extra_env or {}),
    }
    completed = subprocess.run(
        resolved,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if completed.returncode == 0:
        return []
    output = (completed.stdout + "\n" + completed.stderr).strip().splitlines()
    detail = "\n".join(output[-16:])
    return [f"command failed ({' '.join(resolved)}):\n{detail}"]


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

    lock_path = ROOT / "uv.lock"
    try:
        lock = _toml(lock_path)
    except (OSError, ValueError):
        lock = {}
        errors.append("uv.lock must be readable for the coordinated 1.0.0 cut")
    lock_packages = lock.get("package", []) if isinstance(lock, dict) else []
    lock_versions = (
        {
            str(row.get("name")): str(row.get("version"))
            for row in lock_packages
            if isinstance(row, dict) and row.get("name")
        }
        if isinstance(lock_packages, list)
        else {}
    )
    for distribution in COORDINATED_PACKAGES:
        if lock_versions.get(distribution) != "1.0.0":
            errors.append(f"{distribution}: uv.lock must resolve the coordinated version 1.0.0")

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
        if distribution == "edron":
            if "hedron>=1.0.0,<2.0" not in joined:
                errors.append("edron: Hedron dependency must require the canonical 1.x train")
        elif distribution == "edron-sim":
            if "edron>=1.0.0,<2.0" not in joined:
                errors.append("edron-sim: Edron dependency must require the canonical 1.x train")
        elif distribution in PLUGIN_DEFINITION_SATELLITES:
            if "hedron-core>=1.0.0,<2.0" not in joined:
                errors.append(f"{distribution}: composable plugins require hedron-core>=1.0.0,<2.0")
            if distribution == "hedron-notebook" and "hedron>=1.0.0,<2.0" not in joined:
                errors.append("hedron-notebook: flagship dependency must require Hedron 1.x")
        elif (
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
        if (
            not str(row.get("source", "")).strip()
            or not str(row.get("owner", "")).strip()
            or not str(row.get("signature", "")).strip()
        ):
            errors.append(f"task inventory {task} is missing source, signature, or owner")
        try:
            if int(row.get("line", 0)) < 1:
                errors.append(f"task inventory {task} has an invalid source line")
        except (TypeError, ValueError):
            errors.append(f"task inventory {task} has an invalid source line")
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
    build_evidence = json.loads(
        (ACCEPTANCE / "compatibility-report-100/local-build-evidence.json").read_text(
            encoding="utf-8"
        )
    )
    verification = json.loads(
        (ACCEPTANCE / "compatibility-report-100/verification-100.json").read_text(encoding="utf-8")
    )
    workspace = _toml(ROOT / "pyproject.toml")

    if gate.get("phase") != "1.0" or gate.get("target") != "v1.0.0":
        errors.append("1.0 gate must target v1.0.0")
    if gate.get("status") not in {"Planned", "In progress", "Blocked", "Verified"}:
        errors.append("1.0 release gate has an invalid aggregate status")

    rows = gate.get("evidence")
    if not isinstance(rows, list):
        errors.append("release gate must contain evidence rows")
        rows = []
    ids = tuple(str(row.get("id")) for row in rows if isinstance(row, dict))
    if ids != EXPECTED_GATES:
        errors.append(f"unexpected 1.0 gate order/content: {ids!r}")
    states: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            errors.append("release gate contains a non-table evidence row")
            continue
        gate_id = str(row.get("id", "<unknown>"))
        state = str(row.get("state", ""))
        states[gate_id] = state
        if state not in {"Planned", "Blocked", "Verified"}:
            errors.append(f"{gate_id}: invalid evidence state {state!r}")
        if not str(row.get("command", "")).strip():
            errors.append(f"{gate_id}: missing executable command")
        if not str(row.get("owner", "")).strip():
            errors.append(f"{gate_id}: missing owner")

    entry_verified = states.get("ENTRY-100") == "Verified"
    release_verified = states.get("RELEASE-100") == "Verified"
    all_verified = len(states) == len(EXPECTED_GATES) and all(
        state == "Verified" for state in states.values()
    )
    if gate.get("stage_1_entry_satisfied") is not entry_verified:
        errors.append("stage_1_entry_satisfied must match ENTRY-100 evidence state")
    if gate.get("release_cut_satisfied") is not (release_verified and all_verified):
        errors.append("release_cut_satisfied requires every 1.0 evidence row to be Verified")
    if (gate.get("status") == "Verified") is not (release_verified and all_verified):
        errors.append("aggregate status may be Verified only when every gate is Verified")

    if contract.get("status") not in {
        "Implementation in progress; release evidence pending",
        "Blocked",
        "Verified",
    }:
        errors.append("cut contract has an invalid lifecycle status")
    if contract.get("planning_baseline") != "v0.67.0":
        errors.append("cut contract must use immutable v0.67.0 as its baseline")
    if contract.get("changes_runtime") is not True or contract.get("changes_versions") is not True:
        errors.append(
            "1.0 implementation must declare compatibility-preserving runtime corrections "
            "and bump version metadata"
        )
    if contract.get("runtime_change_rule") != (
        "compatibility-preserving corrections only; no net-new Required runtime capabilities"
    ):
        errors.append("1.0 runtime changes must remain compatibility-preserving and non-expansive")
    if contract.get("stage_1_entry_satisfied") is not entry_verified:
        errors.append("cut contract ENTRY-100 state differs from the release gate")
    if contract.get("release_cut_satisfied") is not (release_verified and all_verified):
        errors.append("cut contract release state differs from the release gate")
    if (contract.get("status") == "Verified") is not (release_verified and all_verified):
        errors.append("cut contract may be Verified only when every gate is Verified")
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
        or compatibility.get("status") not in {"blocked", "passed"}
        or not isinstance(compatibility.get("release_claim"), bool)
    ):
        errors.append("compatibility report has invalid identity or lifecycle metadata")
    target_artifact = compatibility.get("target_artifact")
    artifact_available = (
        isinstance(target_artifact, dict) and target_artifact.get("available") is True
    )
    if not isinstance(target_artifact, dict) or not isinstance(
        target_artifact.get("available"), bool
    ):
        errors.append("compatibility report must declare target artifact availability")
    if compatibility.get("release_claim") is True and (
        compatibility.get("status") != "passed" or not artifact_available
    ):
        errors.append("compatibility release claim requires a passed retained target artifact")
    if (
        build_evidence.get("schema") != "hedron.local-build-evidence/1"
        or build_evidence.get("target") != "v1.0.0"
        or not isinstance(build_evidence.get("artifact_retention"), bool)
        or not isinstance(build_evidence.get("release_claim"), bool)
    ):
        errors.append("build evidence has invalid identity or lifecycle metadata")
    if build_evidence.get("release_claim") is True and (
        build_evidence.get("artifact_retention") is not True or not artifact_available
    ):
        errors.append("build release claim requires retained artifacts in the compatibility report")
    reproducibility = build_evidence.get("reproducibility")
    if not isinstance(reproducibility, dict) or reproducibility.get("verified") is not True:
        errors.append("local build evidence must record verified reproducibility")
    artifacts = build_evidence.get("artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 24:
        errors.append("local build evidence must enumerate the 24 coordinated 1.0.0 artifacts")
    else:
        seen_artifacts: set[str] = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                errors.append("local build evidence contains a non-table artifact")
                continue
            name = str(artifact.get("name", ""))
            digest = str(artifact.get("sha256", ""))
            if not name or name in seen_artifacts:
                errors.append("local build evidence contains a missing or duplicate artifact name")
            seen_artifacts.add(name)
            if len(digest) != hashlib.sha256().digest_size * 2 or any(
                char not in "0123456789abcdef" for char in digest
            ):
                errors.append(
                    f"local build evidence has an invalid SHA-256 for {name or '<unknown>'}"
                )
    if (
        verification.get("schema") != "hedron.verification-evidence/1"
        or verification.get("phase") != "1.0"
        or verification.get("target") != "v1.0.0"
        or verification.get("source_commit") != build_evidence.get("source_commit")
        or not isinstance(verification.get("retained_command_output"), bool)
    ):
        errors.append("verification evidence has invalid identity or lifecycle metadata")
    verification_checks = verification.get("checks")
    if not isinstance(verification_checks, list):
        errors.append("verification evidence must contain executable check records")
    else:
        check_ids = {str(row.get("id")) for row in verification_checks if isinstance(row, dict)}
        required_checks = {
            "PHASE-100-UNIT",
            "BRIDGE-100",
            "TYPE-100",
            "QUALITY-100",
            "BROWSER-100",
            "BROWSER-FIREFOX-100",
            "BROWSER-WEBKIT-100",
            "BUILD-100",
            "REGRESS-100",
            "RELEASE-100",
        }
        if check_ids != required_checks:
            errors.append(
                "verification evidence must cover phase, bridge, quality, browser, build, "
                "regression, and release checks"
            )
        for row in verification_checks:
            if not isinstance(row, dict):
                errors.append("verification evidence contains a non-table check")
                continue
            check_id = row.get("id", "<unknown>")
            if not str(row.get("command", "")).strip() or not str(row.get("summary", "")).strip():
                errors.append(f"verification check {check_id} lacks command or summary")
            if str(row.get("status", "")) not in {"passed", "blocked"}:
                errors.append(f"verification check {check_id} has an invalid status")
    bridge_run = compatibility.get("bridge_run")
    if not isinstance(bridge_run, dict):
        errors.append("compatibility report must retain the executable baseline bridge run")
    else:
        if bridge_run.get("baseline_commit") != baseline_commit:
            errors.append("compatibility bridge run must use the recorded immutable baseline")
        facts = bridge_run.get("facts")
        if not isinstance(facts, dict) or facts.get("http_status") != 200:
            errors.append("compatibility bridge run must record a successful canonical HTTP probe")
        for name in ("baseline_typecheck", "current_typecheck"):
            typecheck = bridge_run.get(name)
            if not isinstance(typecheck, dict) or typecheck.get("returncode") != 0:
                errors.append(f"compatibility bridge run must record a successful {name}")

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
    if "Verified" not in str(bom.get("status", "")):
        errors.append("compatibility BOM must retain a Verified bridge status")
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
    for token in (
        "Published as `v1.0.0` on PyPI",
        "RELEASE_1_0",
        "release-gate-1.0.toml",
        "D-117",
    ):
        if token not in roadmap:
            errors.append(f"roadmap does not expose 1.0 packet token {token!r}")

    errors.extend(_check_fixture_corpus())
    errors.extend(_check_package_metadata())
    errors.extend(_check_maintained_consumers())
    errors.extend(_check_inventory_classification(public_inventory, stable_inventory))

    return errors


def _status_blocker(path: Path, label: str) -> list[str]:
    status = str(_toml(path).get("status", ""))
    if any(token in status.lower() for token in ("draft", "pending")):
        return [f"{label} remains incomplete: {status}"]
    return []


def _entry_blockers() -> list[str]:
    findings: list[str] = []
    for filename, label in (
        ("public-inventory-100.toml", "public inventory"),
        ("stable-inventory-100.toml", "stable inventory"),
        ("warnings-100.toml", "warning inventory"),
    ):
        findings.extend(_status_blocker(ACCEPTANCE / filename, label))
    support = (ACCEPTANCE / "support-policy-100.md").read_text(encoding="utf-8")
    if "(draft)" in support.lower():
        findings.append("support policy remains draft and does not publish exact support windows")
    warnings = _toml(ACCEPTANCE / "warnings-100.toml").get("warning", [])
    partial = [
        str(row.get("old_path"))
        for row in warnings
        if isinstance(row, dict) and row.get("confidence") != "complete"
    ]
    if partial:
        findings.append(f"warning coverage is not complete for: {', '.join(partial)}")
    return findings


def _target_artifact_blockers() -> list[str]:
    report = json.loads(
        (ACCEPTANCE / "compatibility-report-100/local-bridge.json").read_text(encoding="utf-8")
    )
    artifact = report.get("target_artifact")
    if not isinstance(artifact, dict) or artifact.get("available") is not True:
        return ["immutable v1.0.0 target artifact is not available"]
    if report.get("status") != "passed" or report.get("release_claim") is not True:
        return ["compatibility report is not approved as release evidence"]
    return []


def verify_gate(gate: str) -> list[str]:
    """Execute the repository-local evidence for one 1.0 gate.

    Passing this command proves the executable slice only. The manifest state
    remains an explicit review decision, and artifact/release gates fail closed
    until immutable evidence is present.
    """
    python = sys.executable
    phase_tests = [
        python,
        "-m",
        "pytest",
        "-q",
        "tests/unit/test_phase_1_0_packet.py",
        "tests/upgrade/test_phase_1_0_fixtures.py",
        "-k",
        "not plan_checker and not release_verification",
    ]
    if gate == "ENTRY-100":
        return _entry_blockers()
    if gate == "SURFACE-100":
        findings = _status_blocker(ACCEPTANCE / "stable-inventory-100.toml", "stable inventory")
        return findings or _run(phase_tests)
    if gate == "REMOVE-100":
        findings = _entry_blockers()
        removal = _toml(ACCEPTANCE / "removal-inventory-100.toml")
        rows = removal.get("removal", [])
        incomplete = [
            str(row.get("old_path"))
            for row in rows
            if isinstance(row, dict) and row.get("state") != "Verified"
        ]
        if incomplete:
            findings.append(f"removal evidence is not Verified for: {', '.join(incomplete)}")
        return findings
    if gate == "MIGRATE-100":
        return _run(
            [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_migrate_api_100.py",
                "tests/unit/test_cli_check_compat.py",
                "tests/upgrade/test_phase_1_0_fixtures.py",
            ]
        )
    if gate == "COMPAT-100":
        findings = _run([python, "scripts/check_upgrade_100.py", "--baseline", "v0.67.0"])
        return findings or _target_artifact_blockers()
    if gate == "INTERACTION-100":
        return _run(phase_tests)
    if gate == "ENGINE-100":
        return _run(
            [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_phase067_capability_inventory.py",
                "tests/conformance/test_component_composition.py",
                "tests/conformance/test_component_model.py",
                "tests/browser/test_htmx_lifecycle.py",
                "tests/browser/test_browser_matrix.py",
                "-n",
                "0",
            ],
            extra_env={"HEDRON_BROWSER": "1"},
        )
    if gate == "TOOLING-100":
        return _run(
            [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_migrate_api_100.py",
                "tests/unit/test_cli_check_compat.py",
                "tests/unit/test_phase063_tooling.py",
            ]
        )
    if gate == "TYPE-100":
        return _run([python, "-m", "pyright", "tests/upgrade/phase_1_0/canonical/app.py"])
    if gate == "SECURITY-100":
        return _run([python, "-m", "pytest", "-q", "tests/security"])
    if gate == "A11Y-100":
        return _run([python, "-m", "pytest", "-q", "tests/a11y"])
    if gate == "PERF-100":
        return _run([python, "-m", "pytest", "-q", "tests/performance"])
    if gate == "FLEET-100":
        return _run(
            [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_package_metadata.py",
                "tests/unit/test_fleet_053.py",
                "tests/ops/test_compose_035.py",
            ]
        )
    if gate == "DOCS-100":
        for command in (
            [python, "scripts/check_docs_train_ssot.py"],
            [python, "scripts/check_public_doc_links.py"],
            [python, "scripts/check_edron_docs.py"],
        ):
            findings = _run(command)
            if findings:
                return findings
        return []
    if gate == "REGRESS-100":
        return _run([python, "-m", "pytest", "-q"])
    if gate == "PKG-100":
        findings = _run(
            [
                python,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_package_metadata.py",
                "tests/ops/test_packaging_isolation.py",
            ]
        )
        return findings or _target_artifact_blockers()
    if gate == "RELEASE-100":
        manifest = _toml(GATE_PATH)
        rows = manifest.get("evidence", [])
        pending = [
            str(row.get("id"))
            for row in rows
            if isinstance(row, dict)
            and row.get("id") != "RELEASE-100"
            and row.get("state") != "Verified"
        ]
        findings = (
            [f"release dependencies are not Verified: {', '.join(pending)}"] if pending else []
        )
        findings.extend(_target_artifact_blockers())
        return findings
    return [f"{gate}: no executable verifier is registered"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-plan", action="store_true", help="validate the 1.0 packet")
    parser.add_argument("--gate", choices=EXPECTED_GATES, help="select one release gate")
    parser.add_argument("--verify", action="store_true", help="require selected release evidence")
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args()

    if args.verify and args.gate is None:
        parser.error("--verify requires --gate")

    errors = check_plan()
    if args.gate and args.verify and not errors:
        errors.extend(verify_gate(args.gate))

    payload = {
        "schema": "hedron.phase-1.0-plan-check/1",
        "ok": not errors,
        "mode": "release-verify" if args.verify else "plan-check",
        "gate": args.gate,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
    else:
        if args.gate and args.verify:
            gate = _toml(GATE_PATH)
            row = next(
                item
                for item in gate["evidence"]
                if isinstance(item, dict) and item.get("id") == args.gate
            )
            print(
                f"{args.gate}: executable evidence passed "
                f"(manifest state remains {row.get('state')})"
            )
        else:
            print(f"Hedron 1.0 packet: OK ({len(EXPECTED_GATES)} gates)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
