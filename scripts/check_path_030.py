#!/usr/bin/env python3
"""PATH-030: WorkbenchPathMiddleware + 0.3.4 path parity (Hedron absent)."""

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
            FWB_PKG / "src" / "fastapi_workbench" / "middleware.py",
            FWB_PKG / "src" / "fastapi_workbench" / "mount.py",
            ROOT / "tests" / "adapters" / "workbench" / "test_path.py",
            ROOT / "tests" / "adapters" / "workbench" / "path_parity_034.json",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    paths = ["tests/adapters/workbench/test_path.py", *workbench_pytest_paths()]
    if run_pytest(list(dict.fromkeys(paths)), "PATH-030"):
        return 1
    print("ok: PATH-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
