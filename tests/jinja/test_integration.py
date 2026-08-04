"""Phase 0.9 Hedron Jinja replacement tests."""

from __future__ import annotations

import pytest
from jinja2 import DictLoader, Environment

from hedron_core import (
    Badge,
    Card,
    HedronError,
    Model,
    RenderMode,
    SafeUrl,
    TrustedHtml,
    UrlPurpose,
)
from hedron_jinja import HedronJinja, TemplateSpec


class DashboardView(Model):
    name: str
    detail: TrustedHtml
    target: SafeUrl


def _view() -> DashboardView:
    return DashboardView(
        name="Ada",
        detail=TrustedHtml.reviewed("<em>Reviewed</em>", source="test"),
        target=SafeUrl.parse("/account", purpose=UrlPurpose.NAVIGATION),
    )


def test_inline_component_and_typed_view() -> None:
    env = Environment(
        loader=DictLoader(
            {"dashboard.html": '<h1>{{ view.name }}</h1>{% hedron "Badge" text=view.name %}'}
        )
    )
    templates = HedronJinja(env, components={"Badge": Badge})
    spec = TemplateSpec("dashboard.html", view_type=DashboardView)

    result = templates.render(spec, _view())

    assert result.mode is RenderMode.FRAGMENT
    assert "<h1>Ada</h1>" in result.html
    assert "hedron-badge" in result.html
    assert result.trace and result.trace["component_invocations"] == 1


def test_explicit_body_and_named_slot() -> None:
    env = Environment(
        loader=DictLoader(
            {
                "card.html": (
                    '{% hedron "Card" title="Profile" with body %}'
                    "<p>{{ view.name }}</p>"
                    '{% slot "footer" %}<a href="{{ view.target|hedron_url }}">Open</a>'
                    "{% endslot %}{% endhedron %}"
                )
            }
        )
    )
    templates = HedronJinja(env, components={"Card": Card})

    result = templates.render("card.html", _view())

    assert '<div class="hedron-card-body"><p>Ada</p></div>' in result.html
    assert '<div class="hedron-card-footer"><a href="/account">Open</a></div>' in result.html


def test_trusted_html_requires_explicit_filter() -> None:
    unsafe_env = Environment(loader=DictLoader({"x.html": "{{ view.detail }}"}))
    unsafe = HedronJinja(unsafe_env)
    with pytest.raises(HedronError) as exc:
        unsafe.render("x.html", _view())
    assert exc.value.diagnostic.code == "HED-JINJA-0009"

    safe_env = Environment(
        loader=DictLoader({"x.html": "{{ view.detail|hedron_trusted }}"})
    )
    safe = HedronJinja(safe_env)
    assert safe.render("x.html", _view()).html == "<em>Reviewed</em>"


def test_component_contract_checked_before_render() -> None:
    env = Environment(loader=DictLoader({"x.html": '{% hedron "Badge" nope="x" %}'}))
    templates = HedronJinja(env, components={"Badge": Badge})

    [diagnostic] = templates.check("x.html")

    assert diagnostic.code == "HED-JINJA-0005"
    assert "unknown props" in diagnostic.explanation


def test_direct_jinja_render_fails_closed() -> None:
    env = Environment(loader=DictLoader({"x.html": '{% hedron "Badge" text="x" %}'}))
    HedronJinja(env, components={"Badge": Badge})

    with pytest.raises(HedronError) as exc:
        env.get_template("x.html").render(view={})

    assert exc.value.diagnostic.code == "HED-JINJA-0006"


def test_output_and_component_limits() -> None:
    output_env = Environment(loader=DictLoader({"x.html": "abcdef"}))
    output = HedronJinja(output_env, max_output_chars=5)
    with pytest.raises(HedronError) as output_exc:
        output.render("x.html", {})
    assert output_exc.value.diagnostic.code == "HED-JINJA-0012"

    component_env = Environment(
        loader=DictLoader(
            {"x.html": '{% hedron "Badge" text="a" %}{% hedron "Badge" text="b" %}'}
        )
    )
    component = HedronJinja(
        component_env,
        components={"Badge": Badge},
        max_component_invocations=1,
    )
    with pytest.raises(HedronError) as component_exc:
        component.render("x.html", {})
    assert component_exc.value.diagnostic.code == "HED-JINJA-0012"


def test_page_and_fragment_shape_policy() -> None:
    page_env = Environment(
        loader=DictLoader(
            {"page.html": "<!DOCTYPE html><html><head></head><body>ok</body></html>"}
        )
    )
    page = HedronJinja(page_env)
    result = page.render(
        TemplateSpec("page.html", mode=RenderMode.PAGE),
        {},
    )
    assert result.mode is RenderMode.PAGE

    fragment_env = Environment(loader=DictLoader({"x.html": "<body>bad</body>"}))
    fragment = HedronJinja(fragment_env)
    with pytest.raises(HedronError) as exc:
        fragment.render("x.html", {})
    assert exc.value.diagnostic.code == "HED-JINJA-0017"
