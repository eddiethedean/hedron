#!/usr/bin/env python3
"""Shared helpers for phase 0.35 gate checkers."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-035.toml"
RELEASE_PACKET = ROOT / "docs" / "acceptance" / "RELEASE_0_35.md"
RFC = ROOT / "docs" / "rfcs" / "RFC-0068-WHOLE-FLEET-CLOSURE.md"
REVIEW_BRIEF = ROOT / "docs" / "acceptance" / "security-review-035" / "BRIEF.md"
IMPLEMENTATION = ROOT / "docs" / "implementation" / "HEDRON_FLEET_035.md"
GATE = ROOT / "docs" / "acceptance" / "release-gate-0.35.toml"
EXPECTED_PACKAGES = (
    "hedron",
    "hedron-core",
    "hedron-explorer",
    "hedron-data",
    "hedron-flask",
    "hedron-django",
    "hedron-jinja",
    "hedron-extras",
    "hedron-conformance",
    "hedron-charts",
    "hedron-native",
    "hedron-sample-kit",
    "hedron-sim",
    "hedron-notebook",
    "hedron-mcp",
    "hedron-gradio",
    "hedron-workbench",
    "hedron-posit",
    "fastapi-workbench",
    "hedron-runtime-node",
    "hedron-runtime-java",
)
VALID_DISPOSITIONS = frozenset({"production_grade", "incubator", "fixture", "eol"})


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def require_inventory_shape(errors: list[str]) -> None:
    if not INVENTORY.is_file():
        errors.append("missing production-grade-inventory-035.toml")
        return
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    if str(data.get("baseline", "")).strip() != "v0.34.0":
        errors.append("inventory baseline must be v0.34.0")
    packages = data.get("packages")
    if not isinstance(packages, list):
        errors.append("inventory missing packages list")
        return
    missing = [name for name in EXPECTED_PACKAGES if name not in packages]
    if missing:
        errors.append(f"inventory missing packages: {missing}")
    for name in packages:
        if not isinstance(name, str):
            errors.append(f"inventory package name must be string: {name!r}")
            continue
        row = data.get(name)
        if not isinstance(row, dict):
            errors.append(f"inventory missing table for {name}")
            continue
        disposition = str(row.get("disposition", "")).strip()
        if disposition not in VALID_DISPOSITIONS:
            errors.append(f"{name}: invalid disposition {disposition!r}")
        if not str(row.get("owner", "")).strip():
            errors.append(f"{name}: owner required")
        if not str(row.get("maturity", "")).strip():
            errors.append(f"{name}: maturity required")


def fail_errors(errors: list[str], label: str) -> int:
    if errors:
        for item in errors:
            print(f"{label}: {item}", file=sys.stderr)
        return 1
    return 0
