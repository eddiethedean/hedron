#!/usr/bin/env python3
"""CONTRACT-028: charts/native production-grade inventory agrees with docs and install guards."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "acceptance" / "production-grade-inventory-028.toml"
REQUIRED_PACKAGES = (
    "hedron-charts",
    "hedron-native",
)
REQUIRED_OPTIONAL_ADAPTERS = (
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
REQUIRED_DOCS = (
    ROOT / "docs" / "api" / "STABILITY.md",
    ROOT / "docs" / "COMPATIBILITY.md",
    ROOT / "docs" / "guides" / "whats-ready.md",
    ROOT / "docs" / "packages" / "hedron-charts.md",
    ROOT / "docs" / "packages" / "hedron-native.md",
    ROOT / "docs" / "api" / "CHART.md",
    ROOT / "docs" / "rfcs" / "RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md",
    ROOT / "docs" / "acceptance" / "upgrade-fixtures-028.md",
    ROOT / "docs" / "acceptance" / "security-review-028" / "BRIEF.md",
)


def main() -> int:
    errors: list[str] = []
    if not INVENTORY.is_file():
        print(f"missing {INVENTORY.relative_to(ROOT)}", file=sys.stderr)
        return 1

    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    if data.get("baseline") != "v0.27.0":
        errors.append("inventory baseline must be v0.27.0")
    packages = data.get("packages")
    if packages != list(REQUIRED_PACKAGES):
        errors.append(f"packages must be {list(REQUIRED_PACKAGES)!r}, got {packages!r}")

    for name in REQUIRED_PACKAGES:
        section = data.get(name)
        if not isinstance(section, dict):
            errors.append(f"missing [{name}] section")
            continue
        for key in ("supported", "experimental", "excluded"):
            value = section.get(key)
            if not isinstance(value, list):
                errors.append(f"{name}.{key} must be a list")
            elif not value and key != "experimental":
                errors.append(f"{name}.{key} must be non-empty")

    charts = data.get("hedron-charts") or {}
    charts_exp = set(charts.get("experimental") or [])
    for required in ("plotly", "altair", "vega_interactive_hosts", *REQUIRED_OPTIONAL_ADAPTERS):
        if required not in charts_exp:
            errors.append(f"hedron-charts.experimental must include {required}")

    charts_sup = set(charts.get("supported") or [])
    for required in (
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
    ):
        if required not in charts_sup:
            errors.append(f"hedron-charts.supported must include {required}")

    native = data.get("hedron-native") or {}
    native_sup = set(native.get("supported") or [])
    for required in (
        "escape_text",
        "escape_attr",
        "source_builds",
        "fuzz_sanitizer_parity",
        "fallback_absence",
        "fallback_runtime_disable",
    ):
        if required not in native_sup:
            errors.append(f"hedron-native.supported must include {required}")
    native_exc = set(native.get("excluded") or [])
    if "required_for_correctness" not in native_exc:
        errors.append("hedron-native.excluded must include required_for_correctness")

    guards = data.get("install_guards") or {}
    if guards.get("charts_default_enables_interactive") is not False:
        errors.append("install_guards.charts_default_enables_interactive must be false")
    if guards.get("charts_default_enables_optional_adapters") is not False:
        errors.append("install_guards.charts_default_enables_optional_adapters must be false")
    if guards.get("charts_supported_loads_cdn") is not False:
        errors.append("install_guards.charts_supported_loads_cdn must be false")
    if guards.get("native_required_for_correctness") is not False:
        errors.append("install_guards.native_required_for_correctness must be false")
    if guards.get("native_runtime_disable_supported") is not True:
        errors.append("install_guards.native_runtime_disable_supported must be true")

    anchors = data.get("docs_anchors") or {}
    for key, rel in (
        ("stability", "docs/api/STABILITY.md"),
        ("compatibility", "docs/COMPATIBILITY.md"),
        ("whats_ready", "docs/guides/whats-ready.md"),
        ("charts_package", "docs/packages/hedron-charts.md"),
        ("native_package", "docs/packages/hedron-native.md"),
        ("chart_api", "docs/api/CHART.md"),
    ):
        if anchors.get(key) != rel:
            errors.append(f"docs_anchors.{key} must be {rel!r}")

    for path in REQUIRED_DOCS:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: CONTRACT-028 production-grade inventory")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
