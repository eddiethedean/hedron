#!/usr/bin/env python3
"""REGRESS-035: Stage 0 packet presence (full suite at later stages)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_035 import GATE, IMPLEMENTATION, RELEASE_PACKET, fail_errors, require_files  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files([RELEASE_PACKET, IMPLEMENTATION, GATE], errors)
    if fail_errors(errors, "REGRESS-035"):
        return 1
    print("ok: REGRESS-035 (packet refine stub)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
