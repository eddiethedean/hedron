"""Additional HDJ format-v1 evidence for JINJA-09-002."""

from __future__ import annotations

from typing import Any, ClassVar

import pytest
from jinja2 import DictLoader, Environment
from jinja2.ext import do as do_ext
from jinja2.ext import loopcontrols
from jinja2.nativetypes import NativeEnvironment

from hedron_core import (
    AssetRef,
    Badge,
    Card,
    Component,
    Field,
    HedronError,
    Model,
    Props,
    RenderMode,
    SafeUrl,
    Secret,
    TrustedHtml,
    UrlPurpose,
    render,
)
from hedron_jinja import HedronJinja, TemplateSpec
from hedron_jinja.source import PROFILE_FEATURES


def _hdj(
    body: str,
    *,
    kind: str = "fragment",
    profile: str = "standard",
    declarations: str = "",
) -> str:
    extra = f"{declarations.rstrip()}\n" if declarations else ""
    return f'---hdj\nversion = 1\nkind = "{kind}"\nprofile = "{profile}"\n{extra}---\n{body}'


class PanelProps(Props):
    title: str
    code: str = Field(default="", identity=True)
    note: str | None = None
    token: Secret[str] | None = None


class Panel(Component[PanelProps]):
    props_type = PanelProps
    slots: ClassVar[dict[str, str]] = {
        "body": "required",
        "aside": "optional",
        "items": "many",
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def render(self) -> Any:
        from hedron_core.html import html

        parts = [html.h2(self.props.title)]
        if "body" in self._slot_values:
            parts.append(html.div(self._slot_values["body"], class_="body"))
        if "aside" in self._slot_values:
            parts.append(html.aside(self._slot_values["aside"]))
        for item in self._slot_values.get("items", []):
            parts.append(html.li(item))
        return html.section(*parts, class_="panel")


def test_exact_profile_feature_sets() -> None:
    assert PROFILE_FEATURES["minimal"] == frozenset({"web.html", "jinja.core"})
    assert "htmx.core" in PROFILE_FEATURES["standard"]
    assert "web.javascript" in PROFILE_FEATURES["full"]
    assert PROFILE_FEATURES["custom"] == PROFILE_FEATURES["minimal"]


@pytest.mark.parametrize(
    "source",
    [
        '---hdj\nversion = true\nkind = "fragment"\nprofile = "minimal"\n---\nok',
        '---hdj\nversion = 1\nkind = 1\nprofile = "minimal"\n---\nok',
        '---hdj\nversion = 1\nkind = "fragment"\nprofile = "nope"\n---\nok',
        '---hdj\nversion = 1\nkind = "fragment"\nprofile = "minimal"\nunknown = 1\n---\nok',
        '---hdj\nversion = 1\nkind = "fragment"\nprofile = "minimal"\nfeatures = [1]\n---\nok',
    ],
)
def test_prologue_rejects_wrong_types_and_unknown_keys(source: str) -> None:
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))
    with pytest.raises(HedronError) as exc:
        templates.describe("x.hdj")
    assert exc.value.diagnostics[0].code == "HED-JINJA-0018"


def test_minimal_three_field_prologue_renders_literal_html() -> None:
    source = (
        "---hdj\n"
        "version = 1\n"
        'kind = "fragment"\n'
        'profile = "minimal"\n'
        "---\n"
        '<section data-role="hero" aria-label="Greeting">Hello</section>'
    )
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))
    result = templates.render("x.hdj", {})
    assert "Hello" in result.html
    assert 'aria-label="Greeting"' in result.html

    rich = _hdj(
        '<section><my-widget data-x="1"></my-widget></section>',
        profile="full",
    )
    rich_templates = HedronJinja(Environment(loader=DictLoader({"rich.hdj": rich})))
    assert "my-widget" in rich_templates.render("rich.hdj", {}).html


def test_jinja_composition_fixtures() -> None:
    env = Environment(
        loader=DictLoader(
            {
                "base.hdj": _hdj(
                    "{% block content %}base{% endblock %}",
                    profile="standard",
                ),
                "child.hdj": _hdj(
                    '{% extends "base.hdj" %}'
                    "{% block content %}{{ super() }}-{{ view.name }}-"
                    "{% macro greet(who) %}hi {{ who }}{% endmacro %}"
                    "{{ greet(view.name) }}"
                    "{% for row in view.rows %}"
                    "{{ row }}{% if not loop.last %}-{% endif %}"
                    "{% endfor %}"
                    "{%- set ns = namespace(total=1) -%}"
                    "{{ ns.total }}"
                    "{# note #}"
                    "{% endblock %}"
                ),
            }
        )
    )
    templates = HedronJinja(env)
    result = templates.render(
        "child.hdj",
        {"name": "Ada", "rows": ["a", "b"]},
    )
    assert "base-Ada-hi Ada" in result.html
    assert "a-b" in result.html


def test_provider_features_require_configuration_before_bind() -> None:
    bare = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "x.hdj": _hdj(
                        "ok",
                        profile="custom",
                        declarations='features = ["jinja.do", "jinja.loop-controls"]',
                    )
                }
            )
        )
    )
    codes = {item.code for item in bare.check("x.hdj")}
    assert "HED-JINJA-0023" in codes

    configured = Environment(
        loader=DictLoader(
            {
                "x.hdj": _hdj(
                    "{% do [] %}{% for i in [1] %}{% break %}{% endfor %}ok",
                    profile="custom",
                    declarations='features = ["jinja.do", "jinja.loop-controls"]',
                )
            }
        ),
        extensions=[do_ext, loopcontrols],
    )
    templates = HedronJinja(configured)
    assert not [item for item in templates.check("x.hdj") if item.severity.name == "ERROR"]
    assert "ok" in templates.render("x.hdj", {}).html


def test_native_environment_and_stream_are_rejected() -> None:
    with pytest.raises(HedronError) as native:
        HedronJinja(NativeEnvironment(loader=DictLoader({"x.hdj": _hdj("ok")})))
    assert native.value.diagnostics[0].code == "HED-JINJA-0014"

    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": _hdj("ok")})))
    with pytest.raises(HedronError) as streamed:
        templates.environment.get_template("x.hdj").stream()
    assert streamed.value.diagnostics[0].code == "HED-JINJA-0014"


def test_nested_components_in_macros_and_loops_preserve_metadata() -> None:
    source = _hdj(
        "{% macro badge(text) %}"
        '{% hedron "Badge" text=text %}'
        "{% endmacro %}"
        "{% for name in view.names %}"
        "{{ badge(name) }}"
        "{% endfor %}"
        '{% hedron "Card" title="Shell" with body %}'
        '{% hedron "Badge" text="nested" %}'
        "{% endhedron %}"
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source})),
        components={"Badge": Badge, "Card": Card},
    )
    result = templates.render("x.hdj", {"names": ["a", "b"]})
    assert result.html.count('class="hedron-badge') == 3
    assert "hedron-card" in result.html
    assert len(result.identity_map) >= 3


def test_python_and_hdj_builtin_parity() -> None:
    python = render(Badge("Ready", tone="success"), mode=RenderMode.FRAGMENT)
    templates = HedronJinja(
        Environment(
            loader=DictLoader({"x.hdj": _hdj('{% hedron "Badge" text="Ready" tone="success" %}')})
        ),
        components={"Badge": Badge},
    )
    hdj = templates.render("x.hdj", {})
    assert hdj.html == python.html
    assert set(hdj.identity_map) == set(python.identity_map)


def test_component_prop_and_slot_contracts() -> None:
    templates = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "good.hdj": _hdj(
                        '{% hedron "Panel" title="T" code="c1" with body %}'
                        "{% slot 'body' %}Body{% endslot %}"
                        "{% slot 'aside' %}Side{% endslot %}"
                        "{% slot 'items' %}One{% endslot %}"
                        "{% slot 'items' %}Two{% endslot %}"
                        "{% endhedron %}"
                    ),
                    "missing.hdj": _hdj('{% hedron "Panel" title="T" with body %}{% endhedron %}'),
                    "unknown_slot.hdj": _hdj(
                        '{% hedron "Panel" title="T" with body %}'
                        "{% slot 'body' %}Body{% endslot %}"
                        "{% slot 'nope' %}X{% endslot %}"
                        "{% endhedron %}"
                    ),
                }
            )
        ),
        components={"Panel": Panel},
    )
    good = templates.render("good.hdj", {})
    assert "Body" in good.html and "Side" in good.html and "One" in good.html

    with pytest.raises(HedronError):
        templates.render("missing.hdj", {})
    with pytest.raises(HedronError) as unknown:
        templates.render("unknown_slot.hdj", {})
    assert unknown.value.diagnostics[0].code == "HED-JINJA-0007"


def test_conflicting_registered_assets_fail_atomically() -> None:
    source = _hdj(
        "ok",
        declarations='assets = ["a", "b"]\nrequires = ["browser.head-mutation"]',
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source})),
        assets={
            "a": AssetRef(kind="script", href="/static/a.js", attributes={"integrity": "sha256-a"}),
            "b": AssetRef(kind="script", href="/static/a.js", attributes={"integrity": "sha256-b"}),
        },
        allowed_capabilities={"browser.head-mutation"},
    )
    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", {})
    assert exc.value.diagnostics[0].code == "HED-JINJA-0013"


def test_htmx_url_attr_matrix_and_eval_capability() -> None:
    class Links(Model):
        get: SafeUrl
        post: SafeUrl
        push: SafeUrl

    view = Links(
        get=SafeUrl.parse("/a", purpose=UrlPurpose.NAVIGATION),
        post=SafeUrl.parse("/b", purpose=UrlPurpose.FORM_ACTION),
        push=SafeUrl.parse("/c", purpose=UrlPurpose.NAVIGATION),
    )
    source = _hdj(
        '<a hx-get="{{ view.get|hedron_nav_url }}" '
        'hx-post="{{ view.post|hedron_form_url }}" '
        'hx-put="{{ view.post|hedron_form_url }}" '
        'hx-patch="{{ view.post|hedron_form_url }}" '
        'hx-delete="{{ view.post|hedron_form_url }}" '
        'hx-push-url="{{ view.push|hedron_nav_url }}" '
        'hx-replace-url="{{ view.push|hedron_nav_url }}">Go</a>'
    )
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))
    result = templates.render(TemplateSpec("x.hdj", view_type=Links), view)
    assert 'hx-get="/a"' in result.html
    assert 'hx-post="/b"' in result.html

    eval_source = _hdj(
        '<button hx-vals="js:{answer: 42}" hx-trigger="click[ctrlKey]">X</button>',
        declarations='requires = ["htmx.eval"]',
    )
    eval_templates = HedronJinja(
        Environment(loader=DictLoader({"y.hdj": eval_source})),
        allowed_capabilities={"htmx.eval"},
    )
    diagnostics = eval_templates.check("y.hdj")
    assert any(item.code == "HED-JINJA-0026" for item in diagnostics)
    assert eval_templates.capabilities("y.hdj").inferred == frozenset({"htmx.eval"})

    bad_scheme = HedronJinja(
        Environment(loader=DictLoader({"z.hdj": _hdj('<a hx-get="javascript:alert(1)">X</a>')}))
    )
    assert any(item.code == "HED-JINJA-0021" for item in bad_scheme.check("z.hdj"))


def test_adversarial_tojson_markup_and_secret_redaction() -> None:
    class Payload(Model):
        secret: Secret[str]
        html: TrustedHtml

    source = _hdj(
        "<script>const data = {{ view.payload|tojson }};</script>"
        "{{ view.html|hedron_trusted }}"
        "{{ view.secret }}",
        profile="full",
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source})),
        allowed_capabilities={"browser.inline-script"},
    )
    # Missing requires for inline script capability.
    assert any(item.code == "HED-JINJA-0024" for item in templates.check("x.hdj"))

    declared = _hdj(
        "<script>const data = {{ {'ok': true}|tojson }};</script>",
        profile="full",
        declarations='requires = ["browser.inline-script", "htmx.response-scripts"]',
    )
    allowed = HedronJinja(
        Environment(loader=DictLoader({"y.hdj": declared})),
        allowed_capabilities={"browser.inline-script", "htmx.response-scripts"},
    )
    assert "true" in allowed.render("y.hdj", {}).html

    with pytest.raises(HedronError) as secret:
        secret_templates = HedronJinja(
            Environment(
                loader=DictLoader(
                    {
                        "s.hdj": _hdj(
                            "{{ view.secret }}",
                            profile="minimal",
                        )
                    }
                )
            )
        )
        secret_templates.render(
            "s.hdj",
            Payload(
                secret=Secret("top-secret"),
                html=TrustedHtml.reviewed("<b>ok</b>", source="test"),
            ),
        )
    message = str(secret.value)
    assert "top-secret" not in message

    escaped = HedronJinja(Environment(loader=DictLoader({"e.hdj": _hdj("{{ view.payload }}")})))
    escaped_html = escaped.render("e.hdj", {"payload": "<img src=x onerror=alert(1)>"}).html
    assert "&lt;img" in escaped_html
    assert "<img" not in escaped_html

    # Markup remains Jinja's escape-bypass; HDJ's reviewed boundary is TrustedHtml.
    # Typed trust values cannot be laundered through `|safe`.
    with pytest.raises(HedronError) as markup_exc:
        launder = HedronJinja(
            Environment(loader=DictLoader({"m.hdj": _hdj("{{ view.payload|safe }}")}))
        )
        launder.render(
            TemplateSpec("m.hdj", strict=False),
            {"payload": TrustedHtml.reviewed("<b>x</b>", source="test")},
        )
    assert markup_exc.value.diagnostics[0].code in {"HED-JINJA-0009", "HED-JINJA-0021"}
