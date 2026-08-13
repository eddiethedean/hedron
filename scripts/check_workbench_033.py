#!/usr/bin/env python3
"""WORKBENCH-033: Workbench suites still owned after extraction."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "fastapi-workbench" / "pyproject.toml",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "runner.py",
            ROOT / "packages" / "hedron-posit" / "src" / "hedron_posit" / "runner.py",
            ROOT / "docs" / "acceptance" / "RELEASE_0_33.md",
        ],
        errors,
    )
    if fail_errors(errors, "WORKBENCH-033"):
        return 1
    return run_pytest(
        [
            "tests/adapters/workbench/",
            "tests/integration/test_workbench_urls.py",
            "tests/integration/test_workbench_runner.py",
            "tests/security/test_workbench_adversarial.py",
            "tests/unit/test_fastapi_workbench_isolation.py",
            "tests/adapters/fastapi_workbench/",
        ],
        "WORKBENCH-033",
    )


if __name__ == "__main__":
    raise SystemExit(main())
