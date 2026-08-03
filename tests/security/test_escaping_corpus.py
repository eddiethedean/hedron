"""Adversarial security corpus for serializer and security types."""

from __future__ import annotations

import pytest

from hedron_core import (
    HedronError,
    SafeUrl,
    Text,
    TrustedHtml,
    UrlPurpose,
    html,
    render,
)


@pytest.mark.security
@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert(1)</script>",
        '"><img src=x onerror=alert(1)>',
        "a\x00b",
        "<svg onload=alert(1)>",
        "{{constructor.constructor('alert(1)')()}}",
    ],
)
def test_text_escaping_corpus(payload: str) -> None:
    html_out = render(Text(payload)).html
    # Escaped text must not introduce executable markup elements.
    assert "<script>" not in html_out
    assert "<svg" not in html_out
    assert "<img" not in html_out
    if "<" in payload:
        assert "&lt;" in html_out
    # Attribute-like substrings may appear as escaped text; ensure no real attrs.
    assert 'onerror="' not in html_out
    assert "onload='" not in html_out


@pytest.mark.security
def test_attribute_escaping() -> None:
    node = html.span("x", title='"><script>alert(1)</script>')
    out = render(node).html
    assert "<script>" not in out
    assert "&quot;" in out or "&#x27;" in out or "&lt;" in out


@pytest.mark.security
@pytest.mark.parametrize(
    "url",
    [
        "javascript:alert(1)",
        "JAVASCRIPT:alert(1)",
        "vbscript:msgbox(1)",
        "data:text/html,hi",
        "\x00javascript:alert(1)",
    ],
)
def test_dangerous_urls_rejected(url: str) -> None:
    with pytest.raises(HedronError):
        SafeUrl.parse(url, purpose=UrlPurpose.NAVIGATION)


@pytest.mark.security
def test_raw_requires_trusted_html() -> None:
    with pytest.raises(HedronError):
        html.raw("<b>nope</b>")  # type: ignore[arg-type]
    node = html.raw(TrustedHtml.reviewed("<b>ok</b>", source="unit-test"))
    assert render(node).html == "<b>ok</b>"


@pytest.mark.security
def test_href_string_rejected() -> None:
    with pytest.raises(HedronError):
        render(html.a("x", href="javascript:alert(1)"))
