"""SSR-036: fallback markup and DOM ownership regions."""

from __future__ import annotations

from hedron_core.rendering import render
from hedron_elements.example import Example
from hedron_elements.markup import render_element_markup


def test_example_ssr_contains_fallback() -> None:
    result = render(Example(status="Online"))
    html = result.html
    assert "hedron-example" in html
    assert 'data-hedron-server-region="content"' in html
    assert "Online" in html
    assert 'data-hedron-abi="1"' in html


def test_markup_escapes_content() -> None:
    html = render_element_markup(
        tag_name="hedron-example",
        abi_version=1,
        element_id="hedron-example",
        server_content="<script>alert(1)</script>",
    )
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_server_and_local_regions_disjoint() -> None:
    result = render(Example(status="Ready"))
    html = result.html
    assert 'data-hedron-server-region="content"' in html
    assert 'data-hedron-local="toggle"' in html
    assert 'data-hedron-local="panel"' in html
