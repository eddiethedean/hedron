#!/usr/bin/env python3
"""WORKBENCH-033: Workbench suites still owned after extraction (refine stub)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "fastapi-workbench" / "pyproject.toml",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "runner.py",
            ROOT / "docs" / "acceptance" / "RELEASE_0_33.md",
        ],
        errors,
    )
    if fail_errors(errors, "WORKBENCH-033"):
        return 1
    print("ok: WORKBENCH-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
