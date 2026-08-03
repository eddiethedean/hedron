"""Conformance checks mapped to COMPONENT_MODEL acceptance (0.1 subset)."""

from __future__ import annotations

from hedron_core import (
    Card,
    Fragment,
    Page,
    RenderMode,
    Stack,
    Text,
    get_registry,
    html,
    render,
)


def test_compose_text_native_fragments_sequences() -> None:
    tree = Stack(
        Text("one"),
        html.span("two"),
        Fragment(Text("three"), None, [Text("four")]),
    )
    out = render(tree).html
    assert "one" in out and "two" in out and "three" in out and "four" in out


def test_page_and_fragment_modes() -> None:
    page = render(Page(Text("body"), title="T"), mode=RenderMode.PAGE)
    frag = render(Text("body"), mode=RenderMode.FRAGMENT)
    assert page.html.startswith("<!DOCTYPE html>")
    assert not frag.html.startswith("<!DOCTYPE html>")
    assert page.mode is RenderMode.PAGE
    assert frag.mode is RenderMode.FRAGMENT


def test_renderables_have_no_route() -> None:
    assert all(m.route is None for m in get_registry().components())


def test_card_slots() -> None:
    card = Card(Text("body"), header=Text("H"), footer=Text("F"))
    html_out = render(card).html
    assert "hedron-card-header" in html_out
    assert "hedron-card-footer" in html_out
