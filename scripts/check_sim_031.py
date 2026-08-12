#!/usr/bin/env python3
"""SIM-031: offline HTMX sim tooling-grade evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_031 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_supported,
    run_pytest,
)

PKG = ROOT / "packages" / "hedron-sim" / "src" / "hedron_sim"


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            PKG / "subset.py",
            PKG / "static" / "hedron-sim.js",
            ROOT / "docs" / "packages" / "hedron-sim.md",
            ROOT / "tests" / "unit" / "test_sim_031.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-sim",
        (
            "deterministic_offline_fragments",
            "declared_htmx_subset",
            "csp_safe_static_assets",
            "unsupported_feature_failure",
        ),
        errors,
    )
    if fail_errors(errors, "SIM-031"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_hedron_sim.py",
            "tests/unit/test_sim_031.py",
        ],
        "SIM-031",
    )


if __name__ == "__main__":
    raise SystemExit(main())
