#!/usr/bin/env python3
"""COMPOSE-035: Stage 0 packet presence (full matrices land in later stages)."""

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
    if "COMPOSE-035" not in plan and "compose" not in plan.lower():
        errors.append("implementation plan missing compose stage")
    if fail_errors(errors, "COMPOSE-035"):
        return 1
    print("ok: COMPOSE-035 (packet refine stub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
