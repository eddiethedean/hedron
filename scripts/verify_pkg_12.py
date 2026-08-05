#!/usr/bin/env python3
"""Verify phase 0.12 packaging evidence that can run without a public index."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/conformance/test_data_chart_contracts.py",
            "tests/unit/test_column_catalog.py",
            "tests/unit/test_grid_chart_events.py",
            "tests/unit/test_saved_views.py",
            "tests/unit/test_transform_plan.py",
            "tests/unit/test_beginner_charts.py",
            "tests/unit/test_chart_events.py",
            "tests/jinja/test_hdj_0_12.py",
        ],
        [sys.executable, str(ROOT / "scripts" / "asset_audit.py")],
        [sys.executable, str(ROOT / "scripts" / "build_evidence_bundle.py")],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-012 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
