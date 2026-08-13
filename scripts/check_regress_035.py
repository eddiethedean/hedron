#!/usr/bin/env python3
"""REGRESS-035: fleet corpora and docs strict build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "release-gate-0.35.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-035.toml",
        ],
        errors,
    )
    if fail_errors(errors, "REGRESS-035"):
        return 1
    code = run_pytest(
        [
            "tests/ops/test_fleet_035.py",
            "tests/ops/test_solver_035.py",
            "tests/ops/test_compose_035.py",
            "tests/ops/test_supply_035.py",
            "tests/ops/test_packaging_isolation.py",
            "tests/upgrade/test_0_34_to_0_35_fleet.py",
        ],
        "REGRESS-035",
    )
    if code != 0:
        return code
    cmd = [
        "uv",
        "run",
        "--group",
        "docs",
        "mkdocs",
        "build",
        "--strict",
        "-f",
        str(ROOT / "mkdocs.yml"),
    ]
    print("+", *cmd)
    try:
        subprocess.check_call(cmd, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"REGRESS-035 mkdocs failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: REGRESS-035")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
