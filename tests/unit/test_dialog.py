"""Dialog component tests."""

from __future__ import annotations

from pathlib import Path

from hedron_core import Dialog
from hedron_core.rendering import render


def test_dialog_renders_native_dialog() -> None:
    result = render(Dialog("Confirm", "Are you sure?", open=True, element_id="dlg"))
    assert "<dialog" in result.html
    assert 'id="dlg"' in result.html
    assert "Confirm" in result.html
    assert 'formmethod="dialog"' in result.html or 'method="dialog"' in result.html
    assert "open" in result.html


def test_dialog_syncs_native_close_without_interrupting_cancel() -> None:
    markup = render(Dialog("Confirm", "Are you sure?")).html
    assert 'x-on:close="open = false"' in markup
    assert "x-on:cancel=" not in markup


def test_dialog_rejects_ids_that_break_ui_openers() -> None:
    import pytest

    with pytest.raises(ValueError, match="must match"):
        Dialog("T", "B", id="1dlg")
    with pytest.raises(ValueError, match="must match"):
        Dialog("T", "B", id="bad id")


def test_dialog_empty_id_allocates_stable_auto_id() -> None:
    a = render(Dialog("A", "x", id="")).html
    b = render(Dialog("B", "y", id="")).html
    assert 'id="hedron-dialog-' in a
    assert 'id="hedron-dialog-' in b
    assert a != b  # distinct allocations across instances


def test_dialog_styles_reset_inherited_alignment() -> None:
    css = Path("packages/hedron-core/src/hedron_core/static/hedron-default.css").read_text(
        encoding="utf-8"
    )
    dialog_start = css.index("  .hedron-dialog {", css.index("@layer base"))
    dialog_end = css.index("  }", dialog_start) + 3
    assert "text-align: start;" in css[dialog_start:dialog_end]
