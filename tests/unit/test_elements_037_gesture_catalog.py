"""GESTURE-037: gesture-catalog.mjs overlay kinds."""

from __future__ import annotations

import re
from pathlib import Path


def test_gesture_catalog_module_exists() -> None:
    static = (
        Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    )
    module = static / "gesture-catalog.mjs"
    assert module.is_file()
    text = module.read_text(encoding="utf-8")
    assert "GestureOverlayCatalog" in text
    assert "OVERLAY_KINDS" in text


def test_gesture_catalog_kinds() -> None:
    static = (
        Path(__file__).resolve().parents[2] / "packages/hedron-elements/src/hedron_elements/static"
    )
    text = (static / "gesture-catalog.mjs").read_text(encoding="utf-8")
    match = re.search(r"OVERLAY_KINDS\s*=\s*Object\.freeze\(\[(.*?)\]\)", text, re.S)
    assert match is not None
    kinds = re.findall(r'"([^"]+)"', match.group(1))
    assert kinds == [
        "dialog",
        "popover",
        "menu",
        "combobox",
        "tooltip",
        "command",
        "toast",
    ]
