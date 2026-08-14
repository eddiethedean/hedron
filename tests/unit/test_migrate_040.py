"""MIGRATE-040 ReactMigrationMatrix and island reference."""

from __future__ import annotations

from pathlib import Path

from hedron_elements.migrate import DISPOSITIONS, NON_FITS, matrix_rows

ROOT = Path(__file__).resolve().parents[2]
ISLAND = ROOT / "docs" / "implementation" / "react-island-reference"


def test_matrix_covers_all_dispositions() -> None:
    seen = {row.disposition for row in matrix_rows()}
    assert set(DISPOSITIONS) == seen
    assert NON_FITS


def test_island_reference_is_outside_hedron_elements_package() -> None:
    assert ISLAND.is_dir()
    readme = (ISLAND / "README.md").read_text(encoding="utf-8")
    assert "No HTMX region ownership" in readme
    assert (
        "Not** shipped inside" in readme
        or "Not** shipped" in readme
        or "not** shipped" in readme.lower()
        or "Not shipped" in readme
        or "not shipped" in readme.lower()
    )
    mjs = (ISLAND / "island.mjs").read_text(encoding="utf-8")
    assert "hx-target" in mjs
    assert "unmount" in mjs
    assert (ISLAND / "island.d.ts").is_file()
    elements_pkg = ROOT / "packages" / "hedron-elements" / "src" / "hedron_elements"
    assert not (elements_pkg / "react_island.py").exists()
    assert "react-island" not in (elements_pkg / "plugin.py").read_text(encoding="utf-8")
