#!/usr/bin/env python3
"""ELEMENTS-036 evidence checker."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_036 import check_gate  # noqa: E402


def main() -> int:
    return check_gate("ELEMENTS-036")


if __name__ == "__main__":
    raise SystemExit(main())
