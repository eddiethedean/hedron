"""INPUT-051 adversarial signature, URL, high-frequency typeahead."""

from __future__ import annotations

import pytest

from hedron.testing import assert_renders
from hedron_core.builtins import ClipboardCopy
from hedron_extras.editors import SignaturePad, Typeahead
from hedron_extras.image_tools import ImageCompare


def test_signature_byte_budget() -> None:
    html = assert_renders(SignaturePad(max_bytes=1024), contains="hedron-extras-signature")
    assert 'data-max-bytes="1024"' in html
    with pytest.raises(ValueError, match="max_bytes"):
        SignaturePad(max_bytes=0)
    with pytest.raises(ValueError, match="max_bytes"):
        SignaturePad(max_bytes=3_000_000)


def test_javascript_url_and_clipboard_size() -> None:
    with pytest.raises(ValueError):
        ImageCompare("javascript:alert(1)", "/static/b.png")
    html = assert_renders(ClipboardCopy(text="ok"), contains="hedron-clipboard-copy")
    assert "ok" in html or "clipboard" in html.lower()
    with pytest.raises(ValueError, match="budget"):
        Typeahead("q", [f"opt-{i}" for i in range(5_001)])
    with pytest.raises(ValueError, match="data"):
        Typeahead("q", ["a"], source="data:text/plain,hi")
    with pytest.raises(ValueError, match="budget"):
        ClipboardCopy("x" * 100_001)
