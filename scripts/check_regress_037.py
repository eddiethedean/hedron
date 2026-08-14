#!/usr/bin/env python3
"""REGRESS-037 evidence checker."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_037 import check_gate, fail_errors, missing_high_severity_citations  # noqa: E402


def main() -> int:
    if fail_errors(missing_high_severity_citations(), "REGRESS-037"):
        return 1
    return check_gate("REGRESS-037")


if __name__ == "__main__":
    raise SystemExit(main())
