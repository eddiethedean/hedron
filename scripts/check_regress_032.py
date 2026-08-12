#!/usr/bin/env python3
"""REGRESS-032: MCP-017 + 0.32 regression and deny-by-default no-op evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_032 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_excluded,
    require_inventory_experimental,
    run_pytest,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "tests" / "unit" / "test_phase17_mcp.py",
            ROOT / "tests" / "unit" / "test_regress_032.py",
        ],
        errors,
    )
    require_inventory_excluded(
        "hedron-mcp",
        (
            "ambient_component_projection",
            "ambient_route_projection",
            "install_grants_authority",
            "mount_grants_authority",
        ),
        errors,
    )
    require_inventory_experimental(
        "hedron-mcp",
        ("mutating_tools_without_full_evidence",),
        errors,
    )
    if fail_errors(errors, "REGRESS-032"):
        return 1
    return run_pytest(
        [
            "tests/unit/test_phase17_mcp.py",
            "tests/unit/test_regress_032.py",
        ],
        "REGRESS-032",
    )


if __name__ == "__main__":
    raise SystemExit(main())
