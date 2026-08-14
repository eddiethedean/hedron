#!/usr/bin/env python3
"""REGRESS-037 evidence checker."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_037 import check_gate  # noqa: E402


def main() -> int:
    return check_gate("REGRESS-037")


if __name__ == "__main__":
    raise SystemExit(main())
