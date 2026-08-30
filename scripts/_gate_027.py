#!/usr/bin/env python3
"""Shared helpers for phase 0.27 gate checkers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def require_inventory_supported(package: str, keys: tuple[str, ...], errors: list[str]) -> None:
    from hedron_core.compat import tomllib

    inventory = ROOT / "docs" / "acceptance" / "production-grade-inventory-027.toml"
    if not inventory.is_file():
        errors.append("missing production-grade-inventory-027.toml")
        return
    data = tomllib.loads(inventory.read_text(encoding="utf-8"))
    section = data.get(package)
    if not isinstance(section, dict):
        errors.append(f"inventory missing [{package}]")
        return
    supported = set(section.get("supported") or [])
    missing = [key for key in keys if key not in supported]
    if missing:
        errors.append(f"{package} inventory missing Supported keys: {missing}")


def run_pytest(rel_paths: list[str], label: str) -> int:
    cmd = [sys.executable, "-m", "pytest", *rel_paths, "-q", "--tb=short"]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"{label} pytest failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0


def run_script(rel: str, label: str) -> int:
    cmd = [sys.executable, str(ROOT / rel)]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"{label} failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0
