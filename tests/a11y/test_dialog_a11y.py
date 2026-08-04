"""Dialog accessibility smoke."""

from __future__ import annotations

from hedron_core import Dialog
from hedron_core.rendering import render


def test_dialog_has_close_control() -> None:
    html = render(Dialog("Title", "Body")).html
    assert "hedron-dialog" in html
    assert "Close" in html
    assert "hedron-dialog-header" in html
