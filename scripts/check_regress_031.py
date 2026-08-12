#!/usr/bin/env python3
"""REGRESS-031: living-train regression suite for the 0.31 packet."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import run_pytest  # noqa: E402


def main() -> int:
    return run_pytest(
        [
            "tests/unit/test_conformance_031.py",
            "tests/unit/test_sim_031.py",
            "tests/unit/test_notebook_031.py",
            "tests/unit/test_plugin_031.py",
            "tests/unit/test_phase17_notebook.py",
            "tests/unit/migrate_streamlit",
        ],
        "REGRESS-031",
    )


if __name__ == "__main__":
    raise SystemExit(main())
