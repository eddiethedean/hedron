"""SINK-056 evidence."""

from __future__ import annotations

import pytest

from hedron_core.security_plane import TrustCompileError, TrustPurpose, compile_trust


def test_sink_056_purpose_compiler() -> None:
    nav = compile_trust("/home", TrustPurpose.URL_NAVIGATION)
    assert nav.purpose is TrustPurpose.URL_NAVIGATION
    sel = compile_trust("#panel", TrustPurpose.SELECTOR)
    assert sel.value == "#panel"
    html = compile_trust("<b>ok</b>", TrustPurpose.MARKUP_HTML, source="review")
    assert html.purpose is TrustPurpose.MARKUP_HTML
    with pytest.raises(TrustCompileError):
        compile_trust(nav, TrustPurpose.SELECTOR)
    with pytest.raises(TrustCompileError):
        compile_trust("javascript:alert(1)", TrustPurpose.URL_NAVIGATION)
    with pytest.raises(TrustCompileError):
        compile_trust("<script>x</script>", TrustPurpose.MARKUP_SVG)
