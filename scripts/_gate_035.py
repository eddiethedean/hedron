#!/usr/bin/env python3
"""Shared helpers for phase 0.35 gate checkers."""

from __future__ import annotations

import subprocess
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
SUPPLY_DIR = ROOT / "docs" / "acceptance" / "fleet-supply-035"
UPGRADE_FIXTURES = ROOT / "docs" / "acceptance" / "upgrade-fixtures-035.md"
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
REQUIRED_ROW_FIELDS = ("owner", "maturity", "channel", "pin", "evidence", "disposition")


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def require_dirs(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_dir():
            errors.append(f"missing directory {path.relative_to(ROOT)}")


def load_inventory() -> dict:
    return tomllib.loads(INVENTORY.read_text(encoding="utf-8"))


def workspace_package_names() -> set[str]:
    names: set[str] = set()
    for pyproject in (ROOT / "packages").glob("*/pyproject.toml"):
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        names.add(str(data["project"]["name"]))
    for runtime in ("hedron-runtime-node", "hedron-runtime-java"):
        if (ROOT / "packages" / runtime).is_dir():
            names.add(runtime)
    return names


def require_inventory_shape(errors: list[str]) -> None:
    if not INVENTORY.is_file():
        errors.append("missing production-grade-inventory-035.toml")
        return
    data = load_inventory()
    if str(data.get("baseline", "")).strip() != "v0.34.0":
        errors.append("inventory baseline must be v0.34.0")
    if str(data.get("present_034_status", "")).strip() != "deferred_to_fleet_docs_audit":
        errors.append("present_034_status must be deferred_to_fleet_docs_audit")
    gates = data.get("present_034_gates")
    if not isinstance(gates, list) or set(gates) != {"FLEET-035", "DOCS-035"}:
        errors.append("present_034_gates must be [FLEET-035, DOCS-035]")
    packages = data.get("packages")
    if not isinstance(packages, list):
        errors.append("inventory missing packages list")
        return
    missing = [name for name in EXPECTED_PACKAGES if name not in packages]
    if missing:
        errors.append(f"inventory missing packages: {missing}")
    workspace = workspace_package_names()
    uncovered = sorted(workspace - set(packages))
    if uncovered:
        errors.append(f"workspace packages missing from inventory: {uncovered}")
    for name in packages:
        if not isinstance(name, str):
            errors.append(f"inventory package name must be string: {name!r}")
            continue
        row = data.get(name)
        if not isinstance(row, dict):
            errors.append(f"inventory missing table for {name}")
            continue
        for field in REQUIRED_ROW_FIELDS:
            if not str(row.get(field, "")).strip():
                errors.append(f"{name}: {field} required")
        disposition = str(row.get("disposition", "")).strip()
        if disposition not in VALID_DISPOSITIONS:
            errors.append(f"{name}: invalid disposition {disposition!r}")
        maturity = str(row.get("maturity", "")).strip().lower()
        if maturity == "alpha" and disposition not in VALID_DISPOSITIONS:
            errors.append(f"{name}: alpha row lacks disposition")


def rfc_is_accepted(*, allow_draft: bool = False) -> bool:
    if not RFC.is_file():
        return False
    for line in RFC.read_text(encoding="utf-8").splitlines()[:20]:
        if line.strip().lower().startswith("**status:**"):
            lowered = line.lower()
            if "accepted" in lowered:
                return True
            if allow_draft and "draft" in lowered:
                return True
    return False


def run_pytest(rel_paths: list[str], label: str) -> int:
    existing = [rel for rel in rel_paths if (ROOT / rel).exists()]
    if not existing:
        print(f"{label}: no pytest paths present (skipped)", file=sys.stderr)
        return 0
    cmd = [sys.executable, "-m", "pytest", *existing, "-q", "--tb=short"]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"{label} pytest failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0


def fail_errors(errors: list[str], label: str) -> int:
    if errors:
        for item in errors:
            print(f"{label}: {item}", file=sys.stderr)
        return 1
    return 0
