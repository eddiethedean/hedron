#!/usr/bin/env python3
"""FILES-034: bounded artifact transport and cleanup."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import run_pytest  # noqa: E402


def main() -> int:
    return run_pytest(
        [
            "tests/unit/test_gradio_034.py",
            "tests/security/test_gradio_034_adversarial.py",
            "tests/unit/test_phase18_gradio.py",
        ],
        "FILES-034",
    )


if __name__ == "__main__":
    raise SystemExit(main())
