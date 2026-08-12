#!/usr/bin/env python3
"""RUNNER-030: pre-bind launcher, env export, fake rserver-url."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_030 import FWB_PKG, HED_WB_PKG, require_files, run_pytest, workbench_pytest_paths  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            FWB_PKG / "src" / "fastapi_workbench" / "runner.py",
            FWB_PKG / "src" / "fastapi_workbench" / "cli.py",
            HED_WB_PKG / "src" / "hedron_workbench" / "runner.py",
            HED_WB_PKG / "src" / "hedron_workbench" / "cli.py",
            ROOT / "tests" / "integration" / "test_workbench_runner.py",
            ROOT / "tests" / "adapters" / "workbench" / "test_cli.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    paths = [
        "tests/integration/test_workbench_runner.py",
        "tests/adapters/workbench/test_cli.py",
        *workbench_pytest_paths(),
    ]
    if run_pytest(list(dict.fromkeys(paths)), "RUNNER-030"):
        return 1
    print("ok: RUNNER-030")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
