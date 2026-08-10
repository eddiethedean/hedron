#!/usr/bin/env python3
"""DATA-027: bounded data CRUD / sources / spreadsheet evidence."""

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
            ROOT / "docs" / "api" / "DATA.md",
            ROOT / "docs" / "acceptance" / "upgrade-fixtures-027.md",
            ROOT / "tests" / "upgrade" / "test_0_26_0_to_0_27_satellites.py",
        ],
        errors,
    )
    require_inventory_supported(
        "hedron-data",
        (
            "datatable_crud",
            "dataeditor_crud",
            "source_in_memory",
            "source_sqlalchemy",
            "saved_views",
            "spreadsheet_documented_paths",
        ),
        errors,
    )
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if run_script("scripts/smoke_data_027.py", "DATA-027 smoke"):
        return 1
    if run_pytest(
        [
            "tests/upgrade/test_0_26_0_to_0_27_satellites.py::test_data_symbols_importable",
            "tests/unit/test_saved_views.py",
            "tests/unit/test_spreadsheet_io.py",
            "tests/unit/test_sqlalchemy_source.py",
            "tests/adapters/django/test_queryset_datasource.py",
        ],
        "DATA-027",
    ):
        return 1
    print("ok: DATA-027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
