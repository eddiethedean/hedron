"""Tabulator editor hosts must survive self-targeted HTMX swaps."""

from __future__ import annotations

from pathlib import Path

_EDITOR = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "hedron-data"
    / "src"
    / "hedron_data"
    / "assets"
    / "tabulator"
    / "editor.js"
)


def test_tabulator_editor_htmx_lifecycle_includes_swap_target() -> None:
    """Both beforeSwap teardown and afterSwap mounting include their root."""
    text = _EDITOR.read_text(encoding="utf-8")

    assert "function matchingElements(root, selector)" in text
    assert "root.matches && root.matches(selector)" in text
    assert "matchingElements(root, HOST_SELECTOR).forEach" in text
    assert "matchingElements(root, TAG).forEach" in text
    assert 'document.addEventListener("htmx:afterSwap"' in text
    assert 'document.addEventListener("htmx:beforeSwap"' in text
