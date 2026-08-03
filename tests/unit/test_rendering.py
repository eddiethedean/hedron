"""Unit tests for rendering, identity, and composition."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from hedron_core import (
    Card,
    Component,
    Fragment,
    Heading,
    HedronError,
    Page,
    Props,
    RenderContext,
    RenderMode,
    Secret,
    Stack,
    Text,
    get_registry,
    html,
    render,
)
from hedron_core.identifiers import instance_id


class NameProps(Props):
    name: str


class Hello(Component[NameProps]):
    props_type = NameProps

    def __init__(self, name: str) -> None:
        super().__init__(NameProps(name=name))

    def render(self):
        return Text(f"Hello, {self.props.name}")


def test_render_fragment_escapes_text() -> None:
    result = render(Text("<script>alert(1)</script>"))
    assert "<script>" not in result.html
    assert "&lt;script&gt;" in result.html
    assert result.mode is RenderMode.FRAGMENT


def test_render_page_doctype() -> None:
    result = render(Page(Heading("Team"), title="Admin"), mode=RenderMode.PAGE)
    assert result.html.startswith("<!DOCTYPE html>")
    assert "<h2>Team</h2>" in result.html
    assert "<title>Admin</title>" in result.html


def test_component_props_immutable() -> None:
    c = Hello("Ada")
    with pytest.raises((TypeError, ValidationError, AttributeError)):
        c.props.name = "Grace"  # type: ignore[misc]


def test_html_rejects_onclick() -> None:
    with pytest.raises(HedronError) as exc:
        html.button("x", onclick="alert(1)")
    assert exc.value.diagnostic.code == "HED-SEC-0002"


def test_html_requires_safe_url_for_href() -> None:
    with pytest.raises(HedronError) as exc:
        html.a("Home", href="/")
    assert exc.value.diagnostic.code == "HED-SEC-0003"


def test_instance_id_deterministic() -> None:
    a = instance_id({"logical_id": "x", "identity": {"key": "1"}})
    b = instance_id({"logical_id": "x", "identity": {"key": "1"}})
    assert a == b
    assert a.startswith("h-")
    assert len(a) == 22  # h- + 20


def test_secret_cannot_render() -> None:
    with pytest.raises(HedronError) as exc:
        render(Secret("nope"))  # type: ignore[arg-type]
    assert exc.value.diagnostic.code == "HED-SEC-0005"


def test_cycle_detection() -> None:
    class Loop(Component[NameProps]):
        props_type = NameProps

        def __init__(self) -> None:
            super().__init__(NameProps(name="x"))

        def render(self):
            return Loop()

    with pytest.raises(HedronError) as exc:
        render(Loop())
    assert exc.value.diagnostic.code == "HED-RENDER-0012"


def test_registry_no_route_by_default() -> None:
    registry = get_registry()
    metas = list(registry.components())
    assert metas
    assert all(m.route is None for m in metas)


def test_composition_slots_and_fragments() -> None:
    tree = Stack(
        Fragment(Text("a"), Text("b")),
        Card(Text("body"), title="Card"),
    )
    result = render(tree)
    assert "hedron-stack" in result.html
    assert "hedron-card" in result.html
    assert "Card" in result.html


def test_standalone_context() -> None:
    ctx = RenderContext.standalone(locale="fr", theme="default")
    result = render(Text("bonjour"), context=ctx)
    assert result.trace is not None
    assert result.trace["locale"] == "fr"
    assert result.trace["theme"] == "default"
