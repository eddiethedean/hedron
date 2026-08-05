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
    ("payload", "must_contain"),
    [
        ("<script>alert(1)</script>", "&lt;script&gt;"),
        ('"><img src=x onerror=alert(1)>', "&lt;"),
        ("<svg onload=alert(1)>", "&lt;svg"),
        ("a\x00b", "ab"),
        ("{{constructor.constructor('alert(1)')()}}", "{{constructor.constructor"),
    ],
)
def test_text_escaping_corpus(payload: str, must_contain: str) -> None:
    html_out = render(Text(payload)).html
    assert must_contain in html_out
    assert "<script>" not in html_out
    assert "<svg" not in html_out
    assert "<img" not in html_out
    assert "\x00" not in html_out
    if "<" in payload:
        assert "&lt;" in html_out
    assert 'onerror="' not in html_out
    assert "onload='" not in html_out


@pytest.mark.security
def test_attribute_escaping() -> None:
    node = html.span("x", title='"><script>alert(1)</script>')
    out = render(node).html
    assert "<script>" not in out
    assert "&quot;" in out  # quote=True must escape attribute delimiters
    assert "&lt;script&gt;" in out


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
        "java\u200bscript:alert(1)",
        "\ufeffjavascript:alert(1)",
        "\u202ejavascript:alert(1)",
        "java\u200cscript:alert(1)",
        "//evil.example",
        "https://u:p@host.example/",
        "file:///etc/passwd",
        "blob:http://example/uuid",
        "about:blank",
    ],
)
def test_dangerous_urls_rejected(url: str) -> None:
    with pytest.raises(HedronError) as exc:
        SafeUrl.parse(url, purpose=UrlPurpose.NAVIGATION, allow_external=True)
    assert exc.value.diagnostic.code == "HED-SEC-0001"


@pytest.mark.security
def test_local_path_rejects_traversal() -> None:
    from hedron_core.htmx_contract import is_local_path

    assert is_local_path("/ok/path")
    assert not is_local_path("/a/../..")
    assert not is_local_path("/a/../b")
    assert not is_local_path("/a/%2e%2e/b")
    assert not is_local_path("/a/%2E%2E")


@pytest.mark.security
def test_safe_css_selector_rejects_combinators() -> None:
    from hedron_core.htmx_contract import safe_css_selector

    assert safe_css_selector("#main")
    assert safe_css_selector(".panel")
    assert safe_css_selector('[data-id="x"]')
    assert not safe_css_selector("#a, #b")
    assert not safe_css_selector("#a #b")
    assert not safe_css_selector("*")
    assert not safe_css_selector("div > #x")
    assert not safe_css_selector("#x:hover")


@pytest.mark.security
def test_icon_rejects_scheme_smuggled_svg() -> None:
    from hedron_core.icons import register_icon

    with pytest.raises(HedronError) as exc:
        register_icon(
            "evil-zwsp",
            (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<a href="java\u200bscript:alert(1)">x</a></svg>'
            ),
            title="Evil",
            source="unit-test",
        )
    assert exc.value.diagnostic.code == "HED-ICON-0003"


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
def test_htmx_2_attribute_contract() -> None:
    out = render(
        html.form(
            **{
                "hx-disinherit": "hx-target",
                "hx-inherit": "hx-headers",
                "hx-validate": "true",
            }
        )
    ).html
    assert 'hx-disinherit="hx-target"' in out
    assert 'hx-inherit="hx-headers"' in out
    assert 'hx-validate="true"' in out

    for removed in ("hx-sse", "hx-ws", "hx-href"):
        with pytest.raises(HedronError) as exc:
            html.div(**{removed: "/legacy"})
        assert exc.value.diagnostic.code == "HED-HTML-0005"


@pytest.mark.security
def test_srcset_ping_and_hx_push_url_require_safe_urls() -> None:
    with pytest.raises(HedronError) as exc:
        html.img(
            src=SafeUrl.parse("/a.png", purpose=UrlPurpose.ASSET),
            alt="x",
            srcset="javascript:alert(1) 1x",
        )
    assert exc.value.diagnostic.code == "HED-SEC-0003"

    with pytest.raises(HedronError):
        html.a(
            "x",
            href=SafeUrl.parse("/", purpose=UrlPurpose.NAVIGATION),
            ping="javascript:alert(1)",
        )

    with pytest.raises(HedronError):
        html.div(**{"hx-push-url": "javascript:alert(1)"})

    ok = render(
        html.img(
            src=SafeUrl.parse("/a.png", purpose=UrlPurpose.ASSET),
            alt="x",
            srcset="/a.png 1x, /b.png 2x",
        )
    ).html
    assert "srcset=" in ok


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
