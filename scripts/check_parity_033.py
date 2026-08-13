#!/usr/bin/env python3
"""PARITY-033: HedronWorkbench compatibility ownership (refine stub)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _gate_033 import (  # noqa: E402
    fail_errors,
    require_files,
    require_inventory_keys,
    require_inventory_packages,
)


def main() -> int:
    errors: list[str] = []
    require_files(
        [
            ROOT / "packages" / "hedron-workbench" / "pyproject.toml",
            ROOT / "packages" / "hedron-workbench" / "src" / "hedron_workbench" / "app.py",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-033.md",
        ],
        errors,
    )
    require_inventory_packages(("hedron-workbench",), errors)
    require_inventory_keys(
        "hedron-workbench",
        supported=(
            "hedron_workbench_compat_subclass",
            "public_imports_cli_extra",
            "inactive_hedron_parity",
        ),
        errors=errors,
    )
    if fail_errors(errors, "PARITY-033"):
        return 1
    print("ok: PARITY-033")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
