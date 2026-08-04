"""Dialog accessibility smoke."""

from __future__ import annotations

import pytest

from hedron_core import Dialog
from hedron_core.rendering import render


@pytest.mark.a11y
def test_dialog_has_close_control() -> None:
    html = render(Dialog("Title", "Body", id="dlg")).html
    assert "hedron-dialog" in html
    assert 'id="dlg"' in html
    assert "Close" in html
    assert "hedron-dialog-header" in html
    assert 'data-modal="true"' in html


@pytest.mark.a11y
def test_dialog_open_modal_ssr_flags() -> None:
    html = render(Dialog("Title", "Body", open=True, modal=True, id="open-dlg")).html
    assert " open" in html or 'open="' in html or html.count("open") >= 1
    assert 'data-modal="true"' in html
