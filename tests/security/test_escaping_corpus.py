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
    assert "<script>" not in html_out
    assert "<svg" not in html_out
    assert "<img" not in html_out
    if "<" in payload:
        assert "&lt;" in html_out
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
        "javascript%3Aalert(1)",
        "&#106;avascript:alert(1)",
        "java%09script:alert(1)",
    ],
)
def test_dangerous_urls_rejected(url: str) -> None:
    with pytest.raises(HedronError) as exc:
        SafeUrl.parse(url, purpose=UrlPurpose.NAVIGATION)
    assert exc.value.diagnostic.code == "HED-SEC-0001"


@pytest.mark.security
def test_raw_requires_trusted_html() -> None:
    with pytest.raises(HedronError):
        html.raw("<b>nope</b>")  # type: ignore[arg-type]
    node = html.raw(TrustedHtml.reviewed("<b>ok</b>", source="unit-test"))
    assert render(node).html == "<b>ok</b>"


@pytest.mark.security
def test_href_string_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        render(html.a("x", href="javascript:alert(1)"))
    assert exc.value.diagnostic.code == "HED-SEC-0003"


@pytest.mark.security
def test_active_tags_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        html.script("alert(1)")
    assert exc.value.diagnostic.code == "HED-SEC-0009"
    with pytest.raises(HedronError):
        html.style("body{x:1}")
    with pytest.raises(HedronError):
        html.iframe(srcdoc="<img src=x onerror=alert(1)>")


@pytest.mark.security
def test_style_and_srcdoc_attrs_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        html.div(style="background:url(javascript:alert(1))")
    assert exc.value.diagnostic.code == "HED-SEC-0007"


@pytest.mark.security
def test_hx_get_requires_safe_url() -> None:
    with pytest.raises(HedronError) as exc:
        html.div(**{"hx-get": "javascript:alert(1)"})
    assert exc.value.diagnostic.code == "HED-SEC-0003"
    url = SafeUrl.parse("/users", purpose=UrlPurpose.NAVIGATION)
    out = render(html.div(**{"hx-get": url})).html
    assert 'hx-get="/users"' in out


@pytest.mark.security
def test_unknown_attr_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        html.span(foo="bar")
    assert exc.value.diagnostic.code == "HED-HTML-0005"


@pytest.mark.security
def test_meta_refresh_url_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        html.meta(**{"http-equiv": "refresh", "content": "0;url=javascript:alert(1)"})
    assert exc.value.diagnostic.code == "HED-SEC-0008"


@pytest.mark.security
def test_url_purpose_mismatch_on_src() -> None:
    nav = SafeUrl.parse("/x", purpose=UrlPurpose.NAVIGATION)
    with pytest.raises(HedronError) as exc:
        html.img(src=nav, alt="x")
    assert exc.value.diagnostic.code == "HED-SEC-0006"
