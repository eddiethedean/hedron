#!/usr/bin/env python3
"""INTERACTIVE-028: Experimental interactive/optional adapters Verified evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_028 import require_files, require_inventory_experimental, run_pytest  # noqa: E402

OPTIONAL_ADAPTERS = (
    "vega-lite",
    "vega-transform",
    "pydeck",
    "maplibre",
    "folium",
    "geospatial",
    "graphviz",
    "mermaid",
    "chartjs",
    "great-tables",
    "sigma",
    "threejs",
    "echarts",
    "datashader",
    "bokeh",
    "holoviews",
    "pygal",
    "plotly-resample",
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "guides" / "whats-ready.md",
            ROOT / "docs" / "COMPATIBILITY.md",
            ROOT / "packages" / "hedron-charts" / "src" / "hedron_charts" / "optional_adapters.py",
            ROOT / "tests" / "unit" / "test_interactive_028_defaults.py",
        ],
        errors,
    )
    require_inventory_experimental(
        "hedron-charts",
        ("plotly", "altair", "vega_interactive_hosts", *OPTIONAL_ADAPTERS),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(
        ["tests/unit/test_interactive_028_defaults.py"],
        "INTERACTIVE-028",
    ):
        return 1
    print("ok: INTERACTIVE-028 Experimental labels + production-default exclusion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
