#!/usr/bin/env python3
"""VENDOR-034: Hugging Face Space fixtures and translation."""

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
            ROOT / "tests" / "fixtures" / "gradio" / "hf_space_cold_start.json",
            ROOT / "tests" / "fixtures" / "gradio" / "hf_quota_error.json",
        ],
        errors,
    )
    if fail_errors(errors, "VENDOR-034"):
        return 1
    return run_pytest(["tests/unit/test_gradio_034.py"], "VENDOR-034")


if __name__ == "__main__":
    raise SystemExit(main())
