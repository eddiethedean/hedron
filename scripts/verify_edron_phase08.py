#!/usr/bin/env python3
"""Verify the in-tree Edron 0.8 implementation packet."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "edron"
PACKET = ROOT / "docs" / "acceptance" / "EDRON_008.md"
GATES = ROOT / "docs" / "acceptance" / "edron-phase08.toml"
VERSION = "0.8.0"
EXPECTED_IDS = {
    "EDR-08-PROFILE",
    "EDR-08-EDGE",
    "EDR-08-HOST",
    "EDR-08-OPS",
    "EDR-08-SUPPLY",
    "EDR-08-UPGRADE",
    "EDR-08-REGRESSION",
}


def main() -> int:
    problems: list[str] = []
    project = tomllib.loads((PACKAGE / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    source = (PACKAGE / "src" / "edron" / "__init__.py").read_text(encoding="utf-8")
    if project.get("version") != VERSION or f'__version__ = "{VERSION}"' not in source:
        problems.append("package version is not 0.8.0")
    dependencies = set(str(item) for item in project.get("dependencies", []))
    for expected in ("hedron>=0.66.2,<0.67", "hedron-data>=0.66.2,<0.67"):
        if expected not in dependencies:
            problems.append(f"0.8.0 dependency pin is missing: {expected}")
    gate = tomllib.loads(GATES.read_text(encoding="utf-8"))
    rows = gate.get("gate", [])
    ids = {row.get("id") for row in rows}
    if gate.get("phase") != "0.8" or gate.get("status") != "Implemented":
        problems.append("machine packet is not marked implemented phase 0.8")
    if ids != EXPECTED_IDS or any(row.get("state") != "Implemented" for row in rows):
        problems.append("machine packet gate IDs or states drifted")
    human_ids = set(re.findall(r"\| `(EDR-08-[A-Z]+)` \|", PACKET.read_text(encoding="utf-8")))
    if human_ids != EXPECTED_IDS:
        problems.append("human packet gate IDs drifted")
    for relative in (
        "src/edron/deployment.py",
        "src/edron/cli/main.py",
        "src/edron/tooling.py",
    ):
        if not (PACKAGE / relative).is_file():
            problems.append(f"missing release file: {relative}")
    if problems:
        print("Edron phase 0.8 verification failed:", file=sys.stderr)
        print("\n".join(f"- {problem}" for problem in problems), file=sys.stderr)
        return 1
    print("ok: Edron phase 0.8 packet and implementation surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
