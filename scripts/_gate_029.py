"""Shared helpers for phase 0.29 gate checkers."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-029.toml"


def require_files(paths: list[Path], errors: list[str]) -> None:
    for path in paths:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")


def run_pytest(rel_paths: list[str], label: str) -> int:
    cmd = [sys.executable, "-m", "pytest", *rel_paths, "-q", "--tb=short"]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"{label} pytest failed ({exc.returncode})", file=sys.stderr)
        return 1
    return 0
