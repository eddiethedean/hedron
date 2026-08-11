#!/usr/bin/env python3
"""CHARTS-028: static/beginner Supported chart inventory Verified evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_028 import require_files, require_inventory_supported, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "api" / "CHART.md",
            ROOT / "docs" / "packages" / "hedron-charts.md",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-028.md",
            ROOT / "docs" / "rfcs" / "RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md",
            ROOT / "tests" / "unit" / "test_charts_028_static_matrix.py",
            ROOT / "tests" / "security" / "test_chart_svg_corpus.py",
            ROOT / "tests" / "upgrade" / "test_0_27_0_to_0_28_charts_native.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-charts",
        (
            "matplotlib_static_svg_png",
            "beginner_line_chart_static",
            "beginner_bar_chart_static",
            "beginner_area_chart_static",
            "beginner_scatter_chart_static",
            "accessible_tabular_text_alternatives",
            "csp_safe_local_assets",
            "bounded_payloads",
            "lifecycle_cleanup",
            "browser_print_export_evidence",
        ),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(
        [
            "tests/unit/test_charts_028_static_matrix.py",
            "tests/security/test_chart_svg_corpus.py",
            "tests/unit/test_beginner_charts.py",
            "tests/upgrade/test_0_27_0_to_0_28_charts_native.py",
        ],
        "CHARTS-028",
    ):
        return 1
    print("ok: CHARTS-028 static/beginner Supported inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
