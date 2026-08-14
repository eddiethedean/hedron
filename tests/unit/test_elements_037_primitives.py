"""PRIMITIVES-037: disclosure and dialog SSR markup."""

from __future__ import annotations

from hedron_core.rendering import render
from hedron_elements.dialog import Dialog
from hedron_elements.disclosure import Disclosure


def test_disclosure_ssr_native_fallback() -> None:
    html = render(Disclosure(summary="More info", open=True)).html
    assert "hedron-disclosure" in html
    assert "<details" in html
    assert "<summary>" in html
    assert "More info" in html
    assert 'data-hedron-server-region="content"' in html


def test_dialog_ssr_native_fallback() -> None:
    html = render(Dialog(title="Confirm", open=True)).html
    assert "hedron-dialog" in html
    assert "<dialog" in html
    assert "Confirm" in html
    assert 'data-hedron-server-region="content"' in html
