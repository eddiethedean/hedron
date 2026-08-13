#!/usr/bin/env python3
"""SUPPLY-035: Stage 0 security BRIEF presence (full supply evidence at cut)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import REVIEW_BRIEF, fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files([REVIEW_BRIEF], errors)
    if fail_errors(errors, "SUPPLY-035"):
        return 1
    print("ok: SUPPLY-035 (packet refine stub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
