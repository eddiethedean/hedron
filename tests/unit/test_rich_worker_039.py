"""RICH-039 / WORKER-039 evidence."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_data.editor import TAG_NAME

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "acceptance" / "rich-surface-inventory-039.toml"
EDITOR_JS = (
    ROOT / "packages" / "hedron-data" / "src" / "hedron_data" / "assets" / "tabulator" / "editor.js"
)


def test_rich_039_owned_experimental_exceptions() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    rich = data["rich"]
    assert rich["experimental_policy"] == "owner_and_destination_required"
    exceptions = rich.get("exceptions")
    assert isinstance(exceptions, list) and len(exceptions) >= 5
    for row in exceptions:
        assert row.get("owner")
        assert row.get("destination")
        assert row.get("disposition") == "experimental"


def test_worker_039_editor_aborts_and_keeps_fallback() -> None:
    text = EDITOR_JS.read_text(encoding="utf-8")
    assert "AbortController" in text
    assert "this._abort.abort" in text
    assert "hedron-data-editor-fallback" in text
    assert "data-hedron-fallback" in text
    assert TAG_NAME == "hedron-data-editor"
    assert "new Worker" not in text
    assert "WebAssembly" not in text
