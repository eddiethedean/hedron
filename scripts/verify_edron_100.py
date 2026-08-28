#!/usr/bin/env python3
"""Verify the Edron 1.0 implementation and canonical Hedron 1.0 contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "edron"
PACKET = ROOT / "docs" / "acceptance" / "EDRON_100.md"
GATES = ROOT / "docs" / "acceptance" / "edron-100.toml"
CURRENT_VERSION = "1.0.0"
EXPECTED_IDS = {
    "EDR-100-TRAIN",
    "EDR-100-ROUTES",
    "EDR-100-IDENTITY",
    "EDR-100-INTERACTION",
    "EDR-100-LIFECYCLE",
    "EDR-100-COMPONENTS",
    "EDR-100-DATA-JOBS-CACHE",
    "EDR-100-TOOLING",
    "EDR-100-PACKAGING",
    "EDR-100-REGRESSION",
}


def main() -> int:
    problems: list[str] = []
    project = tomllib.loads((PACKAGE / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    source = (PACKAGE / "src" / "edron" / "__init__.py").read_text(encoding="utf-8")
    dependencies = {str(item) for item in project.get("dependencies", [])}
    version_marker = f'__version__ = "{CURRENT_VERSION}"'
    if project.get("version") != CURRENT_VERSION or version_marker not in source:
        problems.append("Edron 1.0.0 package version is not synchronized")
    for expected in ("hedron>=1.0.0,<2.0", "hedron-data>=1.0.0,<2.0"):
        if expected not in dependencies:
            problems.append(f"Edron 1.0 dependency pin is missing: {expected}")

    gate = tomllib.loads(GATES.read_text(encoding="utf-8"))
    rows = gate.get("gate", [])
    ids = {row.get("id") for row in rows}
    if (
        gate.get("release") != "1.0"
        or gate.get("status") != "Implemented"
        or gate.get("version") != CURRENT_VERSION
        or gate.get("hedron_train") != "1.0.0"
        or gate.get("hedron_requirement") != ">=1.0.0,<2.0"
        or gate.get("hedron_data_requirement") != ">=1.0.0,<2.0"
        or gate.get("canonical_roles") != ["page", "view", "action", "include"]
    ):
        problems.append("machine packet does not declare the Edron/Hedron 1.0 contract")
    if ids != EXPECTED_IDS or any(row.get("state") != "Implemented" for row in rows):
        problems.append("machine packet gate IDs or implementation states drifted")

    human_ids = set(re.findall(r"\| `(EDR-100-[A-Z0-9-]+)` \|", PACKET.read_text(encoding="utf-8")))
    if human_ids != EXPECTED_IDS:
        problems.append("human packet gate IDs drifted")

    runtime = (PACKAGE / "src" / "edron" / "app.py").read_text(encoding="utf-8")
    for forbidden in (
        "build_view_handle",
        "build_command_handle",
        "self.hedron._root_router",
        "self.hedron._sync_root_route",
        "self.hedron.refreshable(",
        "self.hedron.command(",
        "self.hedron.include_feature(",
    ):
        if forbidden in runtime:
            problems.append(f"non-canonical Hedron route path remains: {forbidden}")

    for relative in (
        "packages/edron/src/edron/scaffolds.py",
        "packages/edron/src/edron/migrate/generate.py",
    ):
        generated = (ROOT / relative).read_text(encoding="utf-8")
        for requirement in (
            '"edron>=1.0.0,<2.0"',
            '"hedron>=1.0.0,<2.0"',
            '"hedron-data>=1.0.0,<2.0"',
        ):
            if requirement not in generated:
                problems.append(f"{relative} is missing {requirement}")

    if problems:
        print("Edron 1.0 verification failed:", file=sys.stderr)
        print("\n".join(f"- {problem}" for problem in problems), file=sys.stderr)
        return 1
    print("ok: Edron 1.0.0 uses the canonical Hedron 1.0 contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
