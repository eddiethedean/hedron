#!/usr/bin/env python3
"""RESOLVE-030: pure Workbench resolver corpus (framework-neutral)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import FWB_PKG, require_files, run_pytest, workbench_pytest_paths  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            FWB_PKG / "src" / "fastapi_workbench" / "resolve.py",
            FWB_PKG / "src" / "fastapi_workbench" / "config.py",
            ROOT / "tests" / "adapters" / "workbench" / "test_resolve.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    paths = ["tests/adapters/workbench/test_resolve.py", *workbench_pytest_paths()]
    if run_pytest(list(dict.fromkeys(paths)), "RESOLVE-030"):
        return 1
    print("ok: RESOLVE-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
