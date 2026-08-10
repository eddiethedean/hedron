#!/usr/bin/env python3
"""EXTRAS-027: curated extras + experimental-ui quarantine evidence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_027 import require_files, require_inventory_supported, run_pytest  # noqa: E402


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "docs" / "acceptance" / "extras-quarantine-025.toml",
            ROOT / "docs" / "packages" / "hedron-extras.md",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-extras",
        ("curated_extras_registry",),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    quarantine = [
        sys.executable,
        str(ROOT / "scripts" / "check_extras_025.py"),
    ]
    print("+", *quarantine)
    try:
        subprocess.check_call(quarantine, cwd=ROOT)
    except subprocess.CalledProcessError as exc:
        print(f"EXTRAS-027 quarantine check failed ({exc.returncode})", file=sys.stderr)
        return 1

    if run_pytest(
        [
            "tests/upgrade/test_0_26_0_to_0_27_satellites.py::test_extras_curated_registry_matches_default_exports",
            "tests/unit/test_phase16_extras_pkg.py",
        ],
        "EXTRAS-027",
    ):
        return 1
    print("ok: EXTRAS-027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
