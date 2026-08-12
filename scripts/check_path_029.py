#!/usr/bin/env python3
"""PATH-029: WorkbenchPathMiddleware + 0.3.4 path parity."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_029 import require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "middleware.py",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "app.py",
            ROOT / "tests" / "adapters" / "workbench" / "test_path.py",
            ROOT / "tests" / "adapters" / "workbench" / "path_parity_034.json",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(["tests/adapters/workbench/test_path.py"], "PATH-029"):
        return 1
    print("ok: PATH-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
