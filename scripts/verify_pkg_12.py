#!/usr/bin/env python3
"""Verify phase 0.12 packaging evidence that can run without a public index."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GATE_TESTS = [
    "tests/conformance/test_data_chart_contracts.py",
    "tests/unit/test_column_catalog.py",
    "tests/unit/test_grid_chart_events.py",
    "tests/unit/test_saved_views.py",
    "tests/unit/test_transform_plan.py",
    "tests/unit/test_sqlalchemy_source.py",
    "tests/unit/test_transform_plan_pushdown.py",
    "tests/unit/test_dask_source.py",
    "tests/unit/test_snowflake_source.py",
    "tests/unit/test_data_editor_advanced.py",
    "tests/unit/test_data_editor_collab.py",
    "tests/unit/test_spreadsheet_io.py",
    "tests/unit/test_aggrid_row_models.py",
    "tests/unit/test_beginner_charts.py",
    "tests/unit/test_chart_events.py",
    "tests/unit/test_chart_annotations.py",
    "tests/unit/test_vega_adapters.py",
    "tests/unit/test_map_adapters.py",
    "tests/unit/test_diagram_adapters.py",
    "tests/unit/test_optional_chart_adapters.py",
    "tests/unit/test_chart_runtime_pins.py",
    "tests/jinja/test_hdj_0_12.py",
    "tests/a11y/test_grid_chart_spatial.py",
]


def _assert_extras_pins() -> None:
    text = (ROOT / "packages/hedron/pyproject.toml").read_text(encoding="utf-8")
    for extra, pattern in (
        ("dev", r"hedron-explorer>=0\.12\.0,<0\.13"),
        ("jinja", r"hedron-jinja>=0\.12\.0,<0\.13"),
    ):
        if not re.search(pattern, text):
            raise SystemExit(f"hedron[{extra}] pin must match {pattern}")


def main() -> int:
    _assert_extras_pins()
    commands = [
        [sys.executable, "-m", "pytest", "-q", *GATE_TESTS],
        [sys.executable, str(ROOT / "scripts" / "asset_audit.py")],
        [sys.executable, str(ROOT / "scripts" / "build_evidence_bundle.py")],
        [sys.executable, str(ROOT / "scripts" / "check_release_gate.py"), "0.12.0"],
    ]
    for command in commands:
        print("+", *command)
        subprocess.check_call(command, cwd=ROOT)
    print("ok: PKG-012 local packaging evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
