#!/usr/bin/env python3
"""LIFECYCLE-036 Stage 0 stub — packet presence only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_036 import planned_stub_ok  # noqa: E402


def main() -> int:
    return planned_stub_ok("LIFECYCLE-036")


if __name__ == "__main__":
    raise SystemExit(main())
