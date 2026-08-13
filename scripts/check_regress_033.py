#!/usr/bin/env python3
"""REGRESS-033: Workbench + posit corpora and docs strict build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "release-gate-0.33.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-033.toml",
            ROOT / "docs" / "acceptance" / "realconnect-033" / "RESULT.log",
            ROOT / "docs" / "acceptance" / "realconnect-029" / "RESULT.log",
        ],
        errors,
    )
    if fail_errors(errors, "REGRESS-033"):
        return 1
    code = run_pytest(
        [
            "tests/adapters/posit/",
            "tests/adapters/workbench/",
            "tests/integration/test_workbench_urls.py",
            "tests/integration/test_workbench_runner.py",
            "tests/security/test_workbench_adversarial.py",
            "tests/unit/test_posit_isolation.py",
            "tests/unit/test_workbench_isolation.py",
            "tests/unit/test_fastapi_workbench_isolation.py",
            "tests/upgrade/test_0_32_to_0_33_posit.py",
            "tests/performance/test_posit_033_perf.py",
        ],
        "REGRESS-033",
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
        print(f"REGRESS-033 mkdocs failed ({exc.returncode})", file=sys.stderr)
        return 1
    print("ok: REGRESS-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
