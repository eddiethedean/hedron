#!/usr/bin/env python3
"""SOLVER-035: Stage 0 packet presence (full matrices land in later stages)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import IMPLEMENTATION, RELEASE_PACKET, fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files([RELEASE_PACKET, IMPLEMENTATION], errors)
    plan = IMPLEMENTATION.read_text(encoding="utf-8") if IMPLEMENTATION.is_file() else ""
    if "SOLVER-035" not in plan and "solver" not in plan.lower():
        errors.append("implementation plan missing solver stage")
    if fail_errors(errors, "SOLVER-035"):
        return 1
    print("ok: SOLVER-035 (packet refine stub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
