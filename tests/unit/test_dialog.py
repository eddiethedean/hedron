"""Dialog component tests."""

from __future__ import annotations

from hedron_core import Dialog
from hedron_core.rendering import render


def test_dialog_renders_native_dialog() -> None:
    result = render(Dialog("Confirm", "Are you sure?", open=True, element_id="dlg"))
    assert "<dialog" in result.html
    assert 'id="dlg"' in result.html
    assert "Confirm" in result.html
    assert 'formmethod="dialog"' in result.html or 'method="dialog"' in result.html
    assert "open" in result.html
