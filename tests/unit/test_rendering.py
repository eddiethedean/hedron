"""Unit tests for rendering, identity, registry, and composition."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from hedron_core import (
    Card,
    Component,
    Field,
    Fragment,
    Heading,
    HedronError,
    Page,
    Props,
    RenderContext,
    RenderMode,
    SafeUrl,
    Secret,
    Stack,
    Text,
    UrlPurpose,
    get_registry,
    html,
    register_component,
    render,
    seal_registry,
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


def test_page_can_select_named_theme_and_color_mode() -> None:
    result = render(
        Page(
            Text("themed"),
            data_theme="dark",
            data_hedron_theme="aurora",
        ),
        mode=RenderMode.PAGE,
    )
    assert 'data-theme="dark"' in result.html
    assert 'data-hedron-theme="aurora"' in result.html


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
    assert len(a) == 22


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
            return self

    with pytest.raises(HedronError) as exc:
        render(Loop())
    assert exc.value.diagnostic.code == "HED-RENDER-0012"
    assert "Loop" in str(exc.value) or "hedron" in exc.value.diagnostic.explanation


def test_nested_same_type_is_not_a_cycle() -> None:
    result = render(Stack(Stack(Text("nested"))))
    assert "nested" in result.html


def test_registry_no_route_by_default() -> None:
    registry = get_registry()
    metas = list(registry.components())
    assert metas
    assert all(m.route is None for m in metas)


def test_register_before_seal() -> None:
    register_component(logical_id="test-pkg:mod.Extra", name="Extra", module="mod")
    seal_registry()
    assert get_registry().get("test-pkg:mod.Extra") is not None
    # Idempotent seal
    again = seal_registry()
    assert again.get("test-pkg:mod.Extra") is not None


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


def test_render_context_mount_prefixes_typed_local_url_attributes_once() -> None:
    node = html.div(
        html.a(
            "Status",
            href=SafeUrl.parse("/status", purpose=UrlPurpose.NAVIGATION),
            **{"hx-get": "/status"},
        ),
        html.form(
            action=SafeUrl.parse("/ping", purpose=UrlPurpose.FORM_ACTION),
            method="post",
        ),
        html.img(
            src=SafeUrl.parse("/image.png", purpose=UrlPurpose.ASSET),
            alt="test",
        ),
    )
    result = render(node, context=RenderContext(mount_path="/content/abc"))
    assert 'href="/content/abc/status"' in result.html
    assert 'hx-get="/content/abc/status"' in result.html
    assert 'action="/content/abc/ping"' in result.html
    assert 'src="/content/abc/image.png"' in result.html
    assert "/content/abc/content/abc" not in result.html


def test_render_result_immutable_maps() -> None:
    result = render(Text("x"))
    with pytest.raises(TypeError):
        result.headers["X"] = "1"  # type: ignore[index]


def test_identity_excludes_secret_fields() -> None:
    class SecretProps2(Props):
        user_id: int = Field(identity=True)
        password: str = Field(secret=True)

    class Box2(Component[SecretProps2]):
        props_type = SecretProps2

        def __init__(self, user_id: int, password: str) -> None:
            super().__init__(SecretProps2(user_id=user_id, password=password))

        def render(self):
            return Text("x")

    fields = Box2(1, "hunter2").identity_fields()
    assert fields == {"user_id": 1}
    assert "hunter2" not in str(fields)


def test_depth_limit() -> None:
    # Build a deep native-element tree (avoids component cycle detection).
    node: object = "end"
    for _ in range(10):
        node = html.div(node)
    with pytest.raises(HedronError) as exc:
        render(node, context=RenderContext(locale="en", max_depth=3))
    assert exc.value.diagnostic.code == "HED-RENDER-0009"


def test_same_explicit_key_collides() -> None:
    a = Hello("Ada").key("k")
    b = Hello("Grace").key("k")
    with pytest.raises(HedronError) as exc:
        render([a, b])
    assert exc.value.diagnostic.code == "HED-RENDER-0013"
