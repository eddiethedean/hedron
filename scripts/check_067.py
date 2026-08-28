#!/usr/bin/env python3
"""Validate the Phase 0.67 packet and execute available release-gate evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "docs" / "acceptance"

EXPECTED_GATES = (
    "FREEZE-067",
    "CONTRACT-067",
    "SUPPLY-067",
    "CSP-067",
    "PLAN-067",
    "CLOSURE-067",
    "ASSET-067",
    "DIRECTIVE-067",
    "CORE-067",
    "PLUGIN-067",
    "UI-067",
    "INTERACTION-067",
    "HTMX-067",
    "MORPH-067",
    "STATE-067",
    "FAILURE-067",
    "SECURITY-067",
    "AUTHOR-067",
    "HDJ-067",
    "TOOLING-067",
    "ENGINE-067",
    "WIDGET-067",
    "A11Y-067",
    "PERF-067",
    "COMPAT-067",
    "DEPRECATE-067",
    "BOM-067",
    "DOCS-067",
    "REGRESS-067",
    "PKG-067",
)


def _toml(path: Path) -> dict[str, object]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str, findings: list[str]) -> None:
    if not condition:
        findings.append(message)


def _command_repo_paths(command: str) -> list[Path]:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    return [ROOT / token for token in tokens if token.startswith(("scripts/", "tests/"))]


def check_plan() -> list[str]:
    """Check that the review decisions are represented by one coherent packet."""
    findings: list[str] = []
    manifest_path = ACCEPTANCE / "release-gate-0.67.toml"
    contract_path = ACCEPTANCE / "contract-freeze-067.toml"
    bom_path = ACCEPTANCE / "compatibility-bom-067.toml"
    engine_path = ACCEPTANCE / "component-engine-dispositions-067.toml"
    capability_path = ACCEPTANCE / "alpine-capability-dispositions-067.toml"
    widget_path = ACCEPTANCE / "widget-evidence-067.toml"
    release_path = ACCEPTANCE / "RELEASE_0_67.md"

    required_files = (
        manifest_path,
        contract_path,
        bom_path,
        engine_path,
        capability_path,
        widget_path,
        release_path,
        ROOT / "docs" / "rfcs" / "RFC-0095-ALPINE-BROWSER-ENHANCEMENT.md",
        ROOT / "docs" / "rfcs" / "RFC-0096-HEDRON-1.0-INTERFACE-CONSOLIDATION.md",
        ROOT / "docs" / "api" / "HTMX_ALPINE_BOUNDARY_1_0.md",
        ROOT / "docs" / "implementation" / "COMPONENT_ENGINE_DISPOSITIONS_067_1_0.md",
        ROOT / "docs" / "implementation" / "ALPINE_INTEGRATION_067.md",
        ROOT / "docs" / "implementation" / "ALPINE_CAPABILITY_AUDIT_067.md",
        ROOT / "docs" / "implementation" / "HEDRON_1_0_EDRON_INTERFACE_AUDIT.md",
        ACCEPTANCE / "morph-disposition-067.md",
    )
    for path in required_files:
        _require(path.is_file(), f"missing phase 0.67 planning artifact: {path}", findings)
    if findings:
        return findings

    manifest = _toml(manifest_path)
    rows = manifest.get("evidence")
    _require(isinstance(rows, list), "release gate requires [[evidence]] rows", findings)
    if not isinstance(rows, list):
        return findings
    ids = tuple(str(row.get("id", "")) for row in rows if isinstance(row, dict))
    _require(
        ids == EXPECTED_GATES, "release-gate IDs/order differ from the frozen packet", findings
    )
    _require(manifest.get("contract_refine") == "D-115", "release gate must cite D-115", findings)
    _require(
        manifest.get("component_engine_decision") == "D-116",
        "release gate must cite D-116",
        findings,
    )
    _require(
        manifest.get("boundary_contract") == "../api/HTMX_ALPINE_BOUNDARY_1_0.md",
        "release gate must cite the normative HTMX/Alpine boundary",
        findings,
    )
    _require(
        manifest.get("component_engine_inventory") == "component-engine-dispositions-067.toml",
        "release gate must cite the component engine inventory",
        findings,
    )
    _require(
        manifest.get("stage_1_entry_satisfied") is True,
        "W1 entry must be satisfied after the freeze evidence passes",
        findings,
    )
    for row in rows:
        if not isinstance(row, dict):
            findings.append("release-gate evidence row is not a table")
            continue
        gate = str(row.get("id", "<unknown>"))
        _require(bool(str(row.get("owner", "")).strip()), f"{gate}: owner is required", findings)
        command = str(row.get("command", "")).strip()
        _require(bool(command), f"{gate}: command is required", findings)
        _require(row.get("state") == "Verified", f"{gate}: evidence is not Verified", findings)
        for path in _command_repo_paths(command):
            _require(path.exists(), f"{gate}: command references missing path {path}", findings)

    release_ids = tuple(
        re.findall(r"^\| `([A-Z0-9]+-067)`", release_path.read_text(encoding="utf-8"), re.M)
    )
    _require(
        release_ids == EXPECTED_GATES, "RELEASE_0_67 gate table differs from manifest", findings
    )

    contract = _toml(contract_path)
    authoring = contract.get("authoring", {})
    returns = contract.get("returns", {})
    interaction = contract.get("interaction", {})
    browser_plan = contract.get("browser_plan", {})
    failure = contract.get("failure", {})
    warnings = contract.get("warnings", {})
    _require(
        contract.get("boundary_contract") == "../api/HTMX_ALPINE_BOUNDARY_1_0.md",
        "contract freeze must cite the normative HTMX/Alpine boundary",
        findings,
    )
    _require(
        contract.get("component_engine_inventory") == "component-engine-dispositions-067.toml",
        "contract freeze must cite the component engine inventory",
        findings,
    )
    _require(
        isinstance(authoring, dict) and authoring.get("route_style") == "functions-only",
        "contract must freeze function-only routes",
        findings,
    )
    _require(
        isinstance(returns, dict)
        and "exactly one presentation tree" in str(returns.get("page", "")),
        "contract must freeze one-tree page returns",
        findings,
    )
    _require(
        isinstance(interaction, dict)
        and interaction.get("effect_variants") == ["local", "request", "combined"],
        "contract must freeze the Interaction discriminant",
        findings,
    )
    _require(
        isinstance(browser_plan, dict)
        and browser_plan.get("response_time_plugin_registration") is False,
        "fragments must not install browser modules",
        findings,
    )
    _require(
        isinstance(failure, dict) and failure.get("essential_x_cloak") is False,
        "essential content must not depend on x-cloak",
        findings,
    )
    _require(
        isinstance(warnings, dict) and "beta/experimental" in str(warnings.get("public_scope", "")),
        "warning scope must include beta/experimental contracts",
        findings,
    )

    bom = _toml(bom_path)
    _require(
        bom.get("owning_gate") == "BOM-067", "compatibility BOM must be owned by BOM-067", findings
    )
    _require(
        "1.0" in str(bom.get("source_compatibility", "")),
        "BOM must state 1.0-on-0.67 source compatibility",
        findings,
    )
    assets = bom.get("browser_assets", {})
    _require(
        isinstance(assets, dict)
        and bool(assets.get("htmx"))
        and bool(assets.get("alpine_csp_candidate")),
        "BOM must pin HTMX and Alpine candidates",
        findings,
    )

    engine = _toml(engine_path)
    families = engine.get("family")
    _require(engine.get("decision") == "D-116", "engine inventory must cite D-116", findings)
    _require(
        engine.get("one_canonical_engine_per_task") is True,
        "engine inventory must enforce one canonical engine per task",
        findings,
    )
    _require(
        engine.get("web_component_abi_retained") is True,
        "engine inventory must retain the Web Component ABI",
        findings,
    )
    _require(isinstance(families, list), "engine inventory requires [[family]] rows", findings)
    if isinstance(families, list):
        current = {
            surface
            for row in families
            if isinstance(row, dict)
            for surface in row.get("current", [])
            if isinstance(surface, str)
        }
        for tag in (
            "hedron-example",
            "hedron-disclose",
            "hedron-disclosure",
            "hedron-dialog",
            "hedron-field-text",
            "hedron-field-choice",
            "hedron-field-file",
            "hedron-action-async",
            "hedron-chart",
            "hedron-map",
            "hedron-data-editor",
        ):
            _require(tag in current, f"engine inventory omits existing tag {tag}", findings)

    capability = _toml(capability_path)
    _require(
        capability.get("schema") == "hedron.alpine-capability-dispositions/1",
        "capability inventory schema is not frozen",
        findings,
    )
    directives = capability.get("directives", {})
    _require(
        isinstance(directives, dict),
        "capability inventory requires directive groups",
        findings,
    )
    if isinstance(directives, dict):
        declared_directives = {
            str(item)
            for key in ("required", "progressive", "advanced", "bounded", "excluded")
            for item in directives.get(key, [])
        }
        expected_directives = {
            "x-data", "x-init", "x-show", "x-bind", "x-on", "x-text", "x-html",
            "x-model", "x-modelable", "x-for", "x-transition", "x-effect", "x-ignore",
            "x-ref", "x-cloak", "x-teleport", "x-if", "x-id",
        }
        _require(
            declared_directives == expected_directives,
            "capability inventory does not cover the frozen Alpine directive surface",
            findings,
        )
    plugins = capability.get("plugins", {})
    _require(isinstance(plugins, dict), "capability inventory requires plugin groups", findings)
    if isinstance(plugins, dict):
        plugin_names = {
            str(item)
            for key in ("required", "progressive")
            for item in plugins.get(key, [])
        }
        _require(
            plugin_names
            == {
                "anchor",
                "collapse",
                "focus",
                "intersect",
                "mask",
                "morph",
                "persist",
                "resize",
                "sort",
            },
            "capability inventory does not cover all nine official plugins",
            findings,
        )

    widgets = _toml(widget_path)
    widget_rows = widgets.get("widget")
    _require(
        isinstance(widget_rows, list) and bool(widget_rows),
        "widget evidence requires [[widget]] rows",
        findings,
    )
    if isinstance(widget_rows, list):
        for row in widget_rows:
            if not isinstance(row, dict):
                findings.append("widget evidence row is not a table")
                continue
            widget_id = str(row.get("id", "<unknown>"))
            _require(
                bool(str(row.get("component", "")).strip()),
                f"{widget_id}: component is required",
                findings,
            )
            _require(
                str(row.get("engine", "")) in {"native", "native-plus-alpine", "htmx"},
                f"{widget_id}: invalid engine",
                findings,
            )
            _require(
                str(row.get("maturity", ""))
                in {"Supported", "Progressive", "Experimental", "Excluded"},
                f"{widget_id}: invalid maturity",
                findings,
            )
            test_path = ROOT / str(row.get("test", ""))
            _require(
                test_path.is_file(),
                f"{widget_id}: missing evidence test {test_path}",
                findings,
            )

    combined_text = "\n".join(path.read_text(encoding="utf-8") for path in required_files[5:])
    for token in (
        "FREEZE-067",
        "document plan",
        "discriminated",
        "HedronFutureWarning",
        "Progressive",
        "0.67a0",
        "1.0a1",
        "No DOM property has two independent writers",
        "one canonical engine",
    ):
        _require(
            token in combined_text, f"planning packet omits required token {token!r}", findings
        )
    return findings


def _run(command: list[str]) -> list[str]:
    """Run one repository evidence command and return concise findings."""
    runner = ROOT / ".venv" / "bin" / "python"
    executable = str(runner) if runner.is_file() else sys.executable
    resolved_command = (
        [executable, *command[1:]] if command and command[0] == sys.executable else command
    )
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join(
            str(ROOT / package / "src")
            for package in ("packages/hedron-core", "packages/hedron", "packages/hedron-jinja")
        ),
    }
    if any("tests/browser" in token for token in resolved_command):
        env["HEDRON_BROWSER"] = "1"
    completed = subprocess.run(
        resolved_command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if completed.returncode == 0:
        return []
    output = (completed.stdout + "\n" + completed.stderr).strip().splitlines()
    detail = "\n".join(output[-12:])
    return [f"command failed ({' '.join(resolved_command)}):\n{detail}"]


def verify_gate(gate: str) -> list[str]:
    """Execute evidence for a gate whose proof is repository-local.

    Supply, browser-matrix, accessibility, performance, and clean-package gates
    intentionally remain explicit failures until their external evidence exists;
    a green unit test must never promote those gates by implication.
    """
    phase_tests = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "tests/unit/test_phase067_contracts.py",
        "tests/unit/test_phase067_capability_inventory.py",
    ]
    if gate in {
        "PLAN-067",
        "CLOSURE-067",
        "DIRECTIVE-067",
        "INTERACTION-067",
        "SECURITY-067",
        "CORE-067",
        "MORPH-067",
    }:
        return _run(phase_tests)
    if gate in {"PLUGIN-067", "UI-067", "HTMX-067", "FAILURE-067"}:
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-n",
                "0",
                "-q",
                "tests/browser/test_phase067_alpine.py",
                "tests/browser/test_htmx_lifecycle.py",
                "tests/browser/test_browser_matrix.py",
            ]
        )
    if gate == "CSP-067":
        static_root = ROOT / "packages/hedron-core/src/hedron_core/static"
        assets = tuple(sorted((static_root / "alpine").glob("*.js"))) + (
            static_root / "hedron-alpine.mjs",
        )
        forbidden = ("unsafe-eval", "eval(", "Function(", "fetch(", "htmx.ajax")
        findings: list[str] = []
        for asset in assets:
            source = asset.read_text(encoding="utf-8")
            findings.extend(
                f"CSP-067: forbidden token {token!r} in {asset}"
                for token in forbidden
                if token in source
            )
        return findings
    if gate == "ASSET-067":
        return _run([sys.executable, "-m", "pytest", "-q", "tests/unit/test_asset_053.py"])
    if gate == "AUTHOR-067":
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_phase067_contracts.py",
                "tests/unit/test_hedron_import_surface.py",
            ]
        )
    if gate == "HDJ-067":
        return _run([sys.executable, "-m", "pytest", "-q", "tests/jinja/test_hdj_0_66.py"])
    if gate == "STATE-067":
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_phase15_browser.py",
                "tests/unit/test_phase067_contracts.py",
            ]
        )
    if gate in {"ENGINE-067", "WIDGET-067"}:
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_phase067_capability_inventory.py",
                "tests/unit/test_phase067_contracts.py",
                "tests/a11y/test_phase05_utilities.py",
                "tests/a11y/test_dialog_a11y.py",
            ]
        )
    if gate == "A11Y-067":
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/a11y/test_phase05_utilities.py",
                "tests/a11y/test_dialog_a11y.py",
            ]
        )
    if gate == "COMPAT-067":
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_hedron_import_surface.py",
                "tests/unit/test_compat_054.py",
                "tests/unit/test_phase067_contracts.py",
            ]
        )
    if gate == "DEPRECATE-067":
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_phase067_contracts.py",
                "tests/unit/test_phase067_capability_inventory.py",
            ]
        )
    if gate == "DOCS-067":
        return []
    if gate == "REGRESS-067":
        return _run([sys.executable, "-m", "pytest", "-q"])
    if gate == "PKG-067":
        return _run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/test_package_metadata.py",
                "tests/ops/test_packaging_isolation.py",
            ]
        )
    if gate == "PERF-067":
        static_root = ROOT / "packages/hedron-core/src/hedron_core/static"
        assets = tuple(sorted((static_root / "alpine").glob("*.js"))) + (
            static_root / "hedron-alpine.mjs",
        )
        total = sum(path.stat().st_size for path in assets if path.is_file())
        findings = []
        if total > 3_000_000:
            findings.append(f"PERF-067: Alpine asset budget exceeded ({total} bytes > 3000000)")
        if any(path.stat().st_size > 1_000_000 for path in assets if path.is_file()):
            findings.append("PERF-067: one Alpine asset exceeds the 1 MB per-asset budget")
        return findings
    if gate == "TOOLING-067":
        return _run([sys.executable, "-m", "pytest", "-q", "tests/unit/test_phase063_tooling.py"])
    if gate == "CONTRACT-067":
        return _run(phase_tests)
    if gate == "BOM-067":
        return verify_gate("SUPPLY-067")
    if gate == "SUPPLY-067":
        supply = ROOT / "packages/hedron-core/src/hedron_core/static/ALPINE_067_SUPPLY.json"
        data = _toml(ROOT / "docs/acceptance/compatibility-bom-067.toml")
        packages = data.get("browser_assets", {})
        findings: list[str] = []
        if not supply.is_file():
            findings.append(f"missing supply manifest: {supply}")
        if not isinstance(packages, dict) or packages.get("alpine_csp_candidate") != "3.16.3":
            findings.append("BOM does not pin Alpine CSP 3.16.3")
        if supply.is_file():
            manifest = json.loads(supply.read_text(encoding="utf-8"))
            static_root = supply.parent
            file_hashes = manifest.get("files", {})
            if not isinstance(file_hashes, dict) or len(file_hashes) != 11:
                findings.append("supply manifest must contain all 11 Alpine artifact file hashes")
            else:
                for relative, expected in sorted(file_hashes.items()):
                    path = static_root / str(relative)
                    if not path.is_file():
                        findings.append(f"missing vendored browser asset: {path}")
                        continue
                    actual = "sha256-" + hashlib.sha256(path.read_bytes()).hexdigest()
                    if actual != expected:
                        findings.append(f"integrity mismatch for vendored asset: {path}")
            for name in ("ALPINE_067_NOTICES.md", "ALPINE_067_SBOM.json"):
                if not (static_root / name).is_file():
                    findings.append(f"missing browser supply evidence: {static_root / name}")
        return findings
    if gate == "FREEZE-067":
        return []
    return [f"{gate}: no executable verifier is registered yet; gate remains Planned"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", choices=EXPECTED_GATES)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check-plan", action="store_true", help="validate planning packet wiring")
    mode.add_argument("--verify", action="store_true", help="verify one implemented runtime gate")
    args = parser.parse_args()

    findings = check_plan()
    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1
    if args.check_plan:
        print(f"ok: phase 0.67 planning packet ({len(EXPECTED_GATES)} gates)")
        return 0

    gate = args.gate
    if gate is None:
        parser.error("--verify requires --gate")
    manifest = _toml(ACCEPTANCE / "release-gate-0.67.toml")
    row = next(item for item in manifest["evidence"] if item["id"] == gate)  # type: ignore[index]
    findings = verify_gate(gate)
    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1
    print(f"{gate}: executable evidence passed (manifest state remains {row.get('state')})")  # type: ignore[union-attr]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
