#!/usr/bin/env python3
"""Shared helpers for phase 0.31 gate checkers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hedron_core.compat import tomllib

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-031.toml"


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def require_dirs(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_dir():
            errors.append(f"missing directory {path.relative_to(ROOT)}")


def require_inventory_supported(package: str, keys: tuple[str, ...], errors: list[str]) -> None:
    if not INVENTORY.is_file():
        errors.append("missing production-grade-inventory-031.toml")
        return
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    section = data.get(package)
    if not isinstance(section, dict):
        errors.append(f"inventory missing [{package}]")
        return
    supported = set(section.get("supported") or [])
    missing = [key for key in keys if key not in supported]
    if missing:
        errors.append(f"{package} inventory missing Supported keys: {missing}")


def require_inventory_excluded(package: str, keys: tuple[str, ...], errors: list[str]) -> None:
    if not INVENTORY.is_file():
        errors.append("missing production-grade-inventory-031.toml")
        return
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    section = data.get(package)
    if not isinstance(section, dict):
        errors.append(f"inventory missing [{package}]")
        return
    excluded = set(section.get("excluded") or [])
    missing = [key for key in keys if key not in excluded]
    if missing:
        errors.append(f"{package} inventory missing Excluded keys: {missing}")


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


def run_script(rel: str, label: str, *extra: str) -> int:
    cmd = [sys.executable, str(ROOT / rel), *extra]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"{label} failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0


def fail_errors(errors: list[str], label: str) -> int:
    if errors:
        for item in errors:
            print(f"{label}: {item}", file=sys.stderr)
        return 1
    return 0
