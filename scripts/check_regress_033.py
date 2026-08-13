#!/usr/bin/env python3
"""REGRESS-033: refine stub requiring packet + prior Connect/Workbench evidence paths."""

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
            ROOT / "docs" / "acceptance" / "release-gate-0.33.toml",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-033.toml",
            ROOT / "docs" / "acceptance" / "realconnect-029" / "RESULT.log",
        ],
        errors,
    )
    if fail_errors(errors, "REGRESS-033"):
        return 1
    print("ok: REGRESS-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
