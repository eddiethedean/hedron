#!/usr/bin/env python3
"""SUPPLY-028: chart runtime + native artifact supply-chain Verified evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_028 import require_files, run_pytest  # noqa: E402

SUPPLY_DIR = ROOT / "docs" / "acceptance" / "charts-supply-028"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "COMPATIBILITY.md",
            ROOT / "docs" / "acceptance" / "production-grade-inventory-028.toml",
            ROOT / "docs" / "rfcs" / "RFC-0059-PRODUCTION-GRADE-CHARTS-NATIVE.md",
            ROOT / "packages" / "hedron-charts" / "src" / "hedron_charts" / "pins.py",
            ROOT / "tests" / "unit" / "test_chart_runtime_pins.py",
            SUPPLY_DIR / "LICENSE_INVENTORY.md",
            SUPPLY_DIR / "SBOM_NOTES.md",
            SUPPLY_DIR / "OFFLINE_INSTALL.md",
            ROOT / "docs" / "acceptance" / "native-wheels-028.toml",
        ],
        errors,
    )
    pins_path = ROOT / "packages" / "hedron-charts" / "src" / "hedron_charts" / "pins.py"
    pins_text = pins_path.read_text(encoding="utf-8")
    for name in ("echarts", "mermaid", "maplibre", "plotly", "vega"):
        if f'"{name}"' not in pins_text and f"'{name}'" not in pins_text:
            errors.append(f"pins.py must include runtime pin {name!r}")
    license_text = (SUPPLY_DIR / "LICENSE_INVENTORY.md").read_text(encoding="utf-8")
    for needle in ("matplotlib", "MIT", "Experimental", "Supported"):
        if needle not in license_text:
            errors.append(f"LICENSE_INVENTORY.md missing {needle!r}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_pytest(
        [
            "tests/unit/test_chart_runtime_pins.py",
            "tests/upgrade/test_0_27_0_to_0_28_charts_native.py",
        ],
        "SUPPLY-028",
    ):
        return 1
    print("ok: SUPPLY-028 pins/license/SBOM/offline evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
