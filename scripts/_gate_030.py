"""Shared helpers for phase 0.30 gate checkers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-030.toml"
FWB_PKG = ROOT / "packages" / "fastapi-workbench"
HED_WB_PKG = ROOT / "packages" / "hedron-workbench"


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def workbench_pytest_paths() -> list[str]:
    """Collect shared Workbench corpora; optional dirs are included when present."""
    paths: list[str] = []
    for rel in (
        "tests/adapters/workbench",
        "tests/workbench",
        "tests/unit/test_workbench_isolation.py",
        "tests/unit/test_fastapi_workbench_isolation.py",
    ):
        if (ROOT / rel).exists():
            paths.append(rel)
    return paths


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
