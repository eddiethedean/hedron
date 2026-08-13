#!/usr/bin/env python3
"""EGRESS-034: allowlist, SSRF, and redirect defenses."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_034 import fail_errors, run_pytest  # noqa: E402


def main() -> int:
    if fail_errors([], "EGRESS-034"):
        return 1
    return run_pytest(
        [
            "tests/security/test_gradio_034_adversarial.py",
            "tests/unit/test_gradio_034.py",
        ],
        "EGRESS-034",
    )


if __name__ == "__main__":
    raise SystemExit(main())
