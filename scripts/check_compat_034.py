#!/usr/bin/env python3
"""COMPAT-034: pinned matrix fixtures and upgrade behavior."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import fail_errors, require_files, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "tests" / "fixtures" / "gradio" / "view_api_minimal.json",
            ROOT / "tests" / "fixtures" / "gradio" / "view_api_stream.json",
            ROOT / "packages" / "hedron-gradio" / "pyproject.toml",
        ],
        errors,
    )
    if fail_errors(errors, "COMPAT-034"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_phase18_gradio.py",
            "tests/unit/test_gradio_034.py",
            "tests/upgrade/test_0_33_to_0_34_gradio.py",
        ],
        "COMPAT-034",
    )


if __name__ == "__main__":
    raise SystemExit(main())
