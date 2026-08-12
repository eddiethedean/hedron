#!/usr/bin/env python3
"""RESOLVE-029: pure Workbench resolver corpus."""

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
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "resolve.py",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "config.py",
            ROOT / "tests" / "adapters" / "workbench" / "test_resolve.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(["tests/adapters/workbench/test_resolve.py"], "RESOLVE-029"):
        return 1
    print("ok: RESOLVE-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
