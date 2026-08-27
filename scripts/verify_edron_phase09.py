#!/usr/bin/env python3
"""Verify the in-tree Edron 0.9 implementation and Hedron 0.67 contract."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "edron"
PACKET = ROOT / "docs" / "acceptance" / "EDRON_009.md"
GATES = ROOT / "docs" / "acceptance" / "edron-phase09.toml"
ROADMAP = ROOT / "docs" / "EDRON_ROADMAP.md"
CURRENT_VERSION = "0.9.0"
EXPECTED_IDS = {
    "EDR-09-TRAIN",
    "EDR-09-NATIVE",
    "EDR-09-BROWSER",
    "EDR-09-CLEAN-067",
    "EDR-09-MATURITY",
    "EDR-09-COMPAT",
    "EDR-09-DEPRECATION",
    "EDR-09-PERF",
    "EDR-09-SECURITY",
    "EDR-09-A11Y",
    "EDR-09-PLATFORM",
    "EDR-09-DOCS",
    "EDR-09-UPGRADE",
    "EDR-09-REGRESSION",
}


def main() -> int:
    problems: list[str] = []
    project = tomllib.loads((PACKAGE / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    source = (PACKAGE / "src" / "edron" / "__init__.py").read_text(encoding="utf-8")
    dependencies = {str(item) for item in project.get("dependencies", [])}
    if project.get("version") != CURRENT_VERSION or (
        f'__version__ = "{CURRENT_VERSION}"' not in source
    ):
        problems.append("Edron 0.9.0 package version is not synchronized")
    for expected in ("hedron>=0.67.0,<0.68", "hedron-data>=0.67.0,<0.68"):
        if expected not in dependencies:
            problems.append(f"Edron 0.9.0 dependency pin is missing: {expected}")

    gate = tomllib.loads(GATES.read_text(encoding="utf-8"))
    rows = gate.get("gate", [])
    ids = {row.get("id") for row in rows}
    if (
        gate.get("phase") != "0.9"
        or gate.get("status") != "Implemented"
        or gate.get("version") != "0.9.0"
        or gate.get("hedron_train") != "0.67.0"
        or gate.get("hedron_requirement") != ">=0.67.0,<0.68"
        or gate.get("hedron_lock_target") != "hedron==0.67.0"
        or gate.get("hedron_forward_compatibility_target") != "1.0.0"
        or gate.get("hedron_1_0_dependency_policy")
        != "do-not-declare-before-release-and-verification"
        or gate.get("deprecated_feature_policy") != "warning-and-migration-input-only"
    ):
        problems.append(
            "machine packet does not declare the Edron 0.9 / Hedron 0.67.0 candidate contract"
        )
    if ids != EXPECTED_IDS or any(row.get("state") != "Implemented" for row in rows):
        problems.append("machine packet gate IDs or implementation states drifted")

    human_ids = set(re.findall(r"\| `(EDR-09-[A-Z0-9-]+)` \|", PACKET.read_text(encoding="utf-8")))
    if human_ids != EXPECTED_IDS:
        problems.append("human packet gate IDs drifted")

    roadmap = ROADMAP.read_text(encoding="utf-8")
    for expected in (
        "long-lived `0.x` consolidation on Hedron `0.67.0`",
        "Edron `0.9.0` with `hedron>=0.67.0,<0.68`",
        "lockfile that resolves",
        "`hedron==0.67.0`",
        "Hedron 0.67 feature integration",
        "Deprecated-feature exclusion",
        "deprecated Hedron 0.67 compatibility path",
        "forward-compatible with Hedron `1.0.0`",
        "EDRON_009.md",
    ):
        if expected not in roadmap:
            problems.append(f"roadmap is missing Phase 0.9 evidence: {expected}")

    for relative in (
        "docs/acceptance/EDRON_009.md",
        "docs/acceptance/edron-phase09.toml",
        "docs/acceptance/upgrade-fixtures-09.md",
        "docs/implementation/ALPINE_INTEGRATION_067.md",
        "docs/api/HTMX_ALPINE_BOUNDARY_1_0.md",
    ):
        if not (ROOT / relative).is_file():
            problems.append(f"missing Phase 0.9 release file: {relative}")

    for relative in (
        "packages/edron/src/edron/browser.py",
        "packages/edron/src/edron/interaction.py",
        "packages/edron/src/edron/deprecations.py",
        "scripts/check_edron_09_release.py",
        "tests/unit/test_edron_phase09.py",
    ):
        if not (ROOT / relative).is_file():
            problems.append(f"missing Phase 0.9 implementation file: {relative}")

    runtime_files = sorted((PACKAGE / "src" / "edron").rglob("*.py"))
    runtime_source = "\n".join(
        path.read_text(encoding="utf-8") for path in runtime_files if path.name != "deprecations.py"
    )
    for forbidden in (
        "self.hedron.refreshable(",
        "self.hedron.command(",
        "self.hedron.include_feature(",
        "hedron-disclose",
        "hedron-dialog",
        "hedron-field-text",
        "hedron-field-choice",
        "hedron-field-file",
        "hedron-action-async",
    ):
        if forbidden in runtime_source:
            problems.append(f"deprecated Hedron 0.67 runtime path remains: {forbidden}")

    if problems:
        print("Edron phase 0.9 verification failed:", file=sys.stderr)
        print("\n".join(f"- {problem}" for problem in problems), file=sys.stderr)
        return 1
    print("ok: Edron phase 0.9 implementation and Hedron 0.67.0 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
