#!/usr/bin/env python3
"""HDJ-027: versioned HDJ authoring graduation evidence."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_027 import require_files, require_inventory_supported, run_pytest, run_script  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "api" / "JINJA.md",
            ROOT / "examples" / "hdj-progressive" / "app.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-jinja",
        (
            "hdj_v1",
            "strict_sink_analysis",
            "manifests_assets",
            "component_bindings",
            "async_preparation",
            "host_integration",
        ),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_script("scripts/smoke_hdj_027.py", "HDJ-027 smoke"):
        return 1
    if run_pytest(
        [
            "tests/upgrade/test_0_26_0_to_0_27_satellites.py::test_hdj_v1_prologue_shape",
            "tests/jinja/test_integration.py",
            "tests/jinja/test_hdj_0_11.py",
            "tests/jinja/test_hdj_async_io.py",
        ],
        "HDJ-027",
    ):
        return 1
    print("ok: HDJ-027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
