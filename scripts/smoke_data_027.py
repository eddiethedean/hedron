#!/usr/bin/env python3
"""DATA-027 smoke: import hedron_data and exercise DataTable/SavedView symbols."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    try:
        data = importlib.import_module("hedron_data")
    except Exception as exc:  # noqa: BLE001
        print(f"import hedron_data failed: {exc}", file=sys.stderr)
        return 1

    for name in (
        "DataTable",
        "DataEditor",
        "SavedView",
        "InMemoryDataSource",
        "SQLAlchemyDataSource",
        "import_rows_xlsx",
        "export_rows_xlsx",
    ):
        if not hasattr(data, name):
            errors.append(f"hedron_data missing {name}")

    notes = ROOT / "examples" / "notes-sqlalchemy" / "app.py"
    if not notes.is_file():
        errors.append("missing examples/notes-sqlalchemy/app.py")

    # Construct a minimal in-memory table path without optional snowflake/dask.
    try:
        from hedron_core import render
        from hedron_core.rendering import RenderMode
        from hedron_data import DataTable

        table = DataTable(rows=[{"id": 1, "title": "hello"}])
        html = render(table, mode=RenderMode.FRAGMENT).html
        if "hello" not in html and "id" not in html and "data" not in html.lower():
            if "hedron" not in html.lower() and "table" not in html.lower():
                errors.append("DataTable render produced unexpected empty markup")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"DataTable smoke failed: {exc}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("ok: smoke_data_027")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
