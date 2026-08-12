#!/usr/bin/env python3
"""RUNNER-029: pre-bind launcher, env export, fake rserver-url."""

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
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "runner.py",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "cli.py",
            ROOT / "tests" / "integration" / "test_workbench_runner.py",
            ROOT / "tests" / "adapters" / "workbench" / "test_cli.py",
        ],
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(
        [
            "tests/integration/test_workbench_runner.py",
            "tests/adapters/workbench/test_cli.py",
        ],
        "RUNNER-029",
    ):
        return 1
    print("ok: RUNNER-029")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
