"""HDJ format-v1 and Hedron integration tests."""

from __future__ import annotations

from collections import UserDict

import pytest
from jinja2 import DictLoader, Environment

from hedron_core import (
    AssetRef,
    Badge,
    Card,
    HedronError,
    Model,
    RenderMode,
    SafeUrl,
    TrustedHtml,
    UrlPurpose,
)
from hedron_jinja import HedronJinja, TemplateKind, TemplateSource, TemplateSpec


class DashboardView(Model):
    name: str
    detail: TrustedHtml
    target: SafeUrl
    submit: SafeUrl
    image: SafeUrl


def _view() -> DashboardView:
    return DashboardView(
        name="Ada",
        detail=TrustedHtml.reviewed("<em>Reviewed</em>", source="test"),
        target=SafeUrl.parse("/account", purpose=UrlPurpose.NAVIGATION),
        submit=SafeUrl.parse("/account", purpose=UrlPurpose.FORM_ACTION),
        image=SafeUrl.parse("/static/avatar.png", purpose=UrlPurpose.ASSET),
    )


def _hdj(
    body: str,
    *,
    kind: str = "fragment",
    profile: str = "standard",
    declarations: str = "",
) -> str:
    extra = f"{declarations.rstrip()}\n" if declarations else ""
    return f'---hdj\nversion = 1\nkind = "{kind}"\nprofile = "{profile}"\n{extra}---\n{body}'


def test_prologue_describe_and_line_preservation() -> None:
    env = Environment(loader=DictLoader({"x.hdj": _hdj("{{")}))
    templates = HedronJinja(env)

    declaration = templates.describe("x.hdj")
    [diagnostic] = templates.check("x.hdj")

    assert declaration.kind is TemplateKind.FRAGMENT
    assert declaration.body_start_line == 6
    assert diagnostic.code == "HED-JINJA-0005"
    assert diagnostic.span and diagnostic.span.start_line == 6


@pytest.mark.parametrize(
    "name,source",
    [
        ("x.html", "plain"),
        ("x.hdj", "plain"),
        ("x.hdj", "\ufeff" + _hdj("ok")),
        ("x.hdj", "---hdj\nversion = 1\n"),
    ],
)
def test_loader_rejects_non_hdj_and_invalid_prologues(name: str, source: str) -> None:
    env = Environment(loader=DictLoader({name: source}))
    templates = HedronJinja(env)

    with pytest.raises((HedronError, ValueError)):
        templates.describe(name)


def test_inline_components_share_identity_and_node_state() -> None:
    env = Environment(
        loader=DictLoader(
            {
                "dashboard.hdj": _hdj(
                    "<h1>{{ view.name }}</h1>"
                    '{% hedron "Badge" text=view.name %}'
                    '{% hedron "Badge" text="Second" %}'
                )
            }
        )
    )
    templates = HedronJinja(env, components={"Badge": Badge})

    result = templates.render(TemplateSpec("dashboard.hdj", view_type=DashboardView), _view())

    assert result.mode is RenderMode.FRAGMENT
    assert "<h1>Ada</h1>" in result.html
    assert result.trace and result.trace["component_invocations"] == 2
    assert result.trace["node_count"] >= 2
    assert len(result.identity_map) == 2
    assert len(set(result.identity_map.values())) == 2


def test_explicit_body_named_slot_and_escaping() -> None:
    env = Environment(
        loader=DictLoader(
            {
                "card.hdj": _hdj(
                    '{% hedron "Card" title="Profile" with body %}'
                    "<p>{{ view.name }}</p>"
                    '{% slot "footer" %}'
                    '<a href="{{ view.target|hedron_nav_url }}">Open</a>'
                    "{% endslot %}{% endhedron %}"
                )
            }
        )
    )
    templates = HedronJinja(env, components={"Card": Card})

    result = templates.render("card.hdj", _view())

    assert (
        '<div class="hedron-card-body" data-hedron-component="Card" '
        'data-hedron-part="supporting-copy" data-hedron-state="default"><p>Ada</p></div>'
        in result.html
    )
    assert (
        '<div class="hedron-card-footer" data-hedron-component="Card" '
        'data-hedron-part="metadata" data-hedron-state="default"><a href="/account">Open</a></div>'
        in result.html
    )


def test_trusted_html_is_limited_to_body_content() -> None:
    safe_env = Environment(loader=DictLoader({"x.hdj": _hdj("{{ view.detail|hedron_trusted }}")}))
    assert HedronJinja(safe_env).render("x.hdj", _view()).html == "<em>Reviewed</em>"

    attr_env = Environment(
        loader=DictLoader({"x.hdj": _hdj('<div title="{{ view.detail|hedron_trusted }}"></div>')})
    )
    diagnostics = HedronJinja(attr_env).check("x.hdj")
    assert any(item.code == "HED-JINJA-0021" for item in diagnostics)


def test_context_checker_ignores_jinja_comments_and_rejects_html_comment_data() -> None:
    source_comment = _hdj("{# <script>{{ view.detail|safe }}</script> #}<p>ok</p>")
    assert not HedronJinja(Environment(loader=DictLoader({"x.hdj": source_comment}))).check("x.hdj")

    raw = _hdj("{% raw %}{{ this_is_literal }}{% endraw %}")
    assert not HedronJinja(Environment(loader=DictLoader({"x.hdj": raw}))).check("x.hdj")

    html_comment = _hdj("<!-- {{ view.name }} -->")
    diagnostics = HedronJinja(Environment(loader=DictLoader({"x.hdj": html_comment}))).check(
        "x.hdj"
    )
    assert any(item.code == "HED-JINJA-0021" for item in diagnostics)


def test_template_strict_false_still_rejects_generic_safe() -> None:
    source = _hdj("{{ view.value|safe }}")
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})), strict=False)
    diagnostics = templates.check(TemplateSpec("x.hdj", strict=False))
    assert any(
        "safe" in (item.title or "").lower() or item.code.startswith("HED-JINJA")
        for item in diagnostics
    )
    with pytest.raises(HedronError) as exc:
        templates.render(TemplateSpec("x.hdj", strict=False), {"value": "<em>ok</em>"})
    assert (
        exc.value.diagnostic.code in {"HED-JINJA-0009", "HED-JINJA-0021"}
        or "safe" in str(exc.value).lower()
    )


@pytest.mark.parametrize(
    "attribute,field,filter_name",
    [
        ("href", "target", "hedron_nav_url"),
        ("action", "submit", "hedron_form_url"),
        ("src", "image", "hedron_asset_url"),
        ("srcset", "image", "hedron_asset_url"),
    ],
)
def test_context_specific_safe_url_filters(attribute: str, field: str, filter_name: str) -> None:
    good = _hdj(f'<a {attribute}="{{{{ view.{field}|{filter_name} }}}}">x</a>')
    good_templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": good})))
    assert not good_templates.check("x.hdj")

    bad = _hdj(f'<a {attribute}="{{{{ view.{field} }}}}">x</a>')
    bad_templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": bad})))
    assert any(item.code == "HED-JINJA-0021" for item in bad_templates.check("x.hdj"))


def test_strict_context_handles_script_src_and_rejects_unquoted_attributes() -> None:
    script = _hdj('<script type="module" src="{{ view.image|hedron_asset_url }}"></script>')
    script_templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": script})),
        allowed_capabilities={"network.script-origin:https://cdn.example"},
    )
    assert not any(item.code == "HED-JINJA-0021" for item in script_templates.check("x.hdj"))

    unquoted = _hdj("<a href={{ view.target|hedron_nav_url }}>x</a>")
    unquoted_templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": unquoted})))
    assert any(item.code == "HED-JINJA-0021" for item in unquoted_templates.check("x.hdj"))


def test_url_filter_checks_runtime_purpose() -> None:
    source = _hdj('<form action="{{ view.target|hedron_form_url }}"></form>')
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))

    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", _view())
    assert exc.value.diagnostic.code == "HED-JINJA-0010"

    external_source = _hdj('<a href="{{ view.target|hedron_nav_url }}">external</a>')
    external_templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": external_source})))
    external_view = {
        "target": SafeUrl.parse(
            "https://example.test/account",
            purpose=UrlPurpose.NAVIGATION,
            allow_external=True,
        )
    }
    with pytest.raises(HedronError) as external_exc:
        external_templates.render("x.hdj", external_view)
    assert external_exc.value.diagnostic.code == "HED-JINJA-0010"


def test_component_contract_checked_before_render() -> None:
    env = Environment(loader=DictLoader({"x.hdj": _hdj('{% hedron "Badge" nope="x" %}')}))
    templates = HedronJinja(env, components={"Badge": Badge})

    [diagnostic] = templates.check("x.hdj")

    assert diagnostic.code == "HED-JINJA-0005"
    assert "unknown props" in diagnostic.explanation


def test_lazy_or_custom_view_mappings_are_rejected() -> None:
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": _hdj("ok")})))
    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", UserDict({"name": "Ada"}))
    assert exc.value.diagnostic.code == "HED-JINJA-0008"


def test_all_direct_hdj_rendering_fails_closed() -> None:
    env = Environment(loader=DictLoader({"x.hdj": _hdj("plain HTML")}))
    HedronJinja(env)

    with pytest.raises(HedronError) as exc:
        env.get_template("x.hdj").render(view={})

    assert exc.value.diagnostic.code == "HED-JINJA-0006"


def test_output_and_component_limits() -> None:
    output = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj("abcdef")})),
        max_output_chars=5,
    )
    with pytest.raises(HedronError) as output_exc:
        output.render("x.hdj", {})
    assert output_exc.value.diagnostic.code == "HED-JINJA-0012"

    component = HedronJinja(
        Environment(
            loader=DictLoader(
                {"x.hdj": _hdj('{% hedron "Badge" text="a" %}{% hedron "Badge" text="b" %}')}
            )
        ),
        components={"Badge": Badge},
        max_component_invocations=1,
    )
    with pytest.raises(HedronError) as component_exc:
        component.render("x.hdj", {})
    assert component_exc.value.diagnostic.code == "HED-JINJA-0012"

    metadata = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj('{% hedron "Badge" text="a" %}')})),
        components={"Badge": Badge},
        max_metadata_items=1,
    )
    with pytest.raises(HedronError) as metadata_exc:
        metadata.render("x.hdj", {})
    assert metadata_exc.value.diagnostic.code == "HED-JINJA-0012"

    with pytest.raises(ValueError, match="must be positive"):
        HedronJinja(
            Environment(loader=DictLoader({"x.hdj": _hdj("ok")})),
            max_output_chars=0,
        )


def test_async_environment_rejects_sync_render() -> None:
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj("ok")}), enable_async=True)
    )
    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", {})
    assert exc.value.diagnostic.code == "HED-JINJA-0014"


@pytest.mark.anyio
async def test_async_render_requires_explicit_feature() -> None:
    undeclared = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj("ok")}), enable_async=True)
    )
    with pytest.raises(HedronError) as exc:
        await undeclared.render_async("x.hdj", {})
    assert exc.value.diagnostic.code == "HED-JINJA-0023"

    declared = HedronJinja(
        Environment(
            loader=DictLoader({"x.hdj": _hdj("ok", declarations='features = ["jinja.async"]')}),
            enable_async=True,
        )
    )
    assert (await declared.render_async("x.hdj", {})).html == "ok"


def test_source_kind_is_authoritative() -> None:
    page_source = _hdj("<!DOCTYPE html><html><head></head><body>ok</body></html>", kind="page")
    page = HedronJinja(Environment(loader=DictLoader({"page.hdj": page_source})))
    result = page.render(TemplateSpec("page.hdj", mode=RenderMode.PAGE), {})
    assert result.mode is RenderMode.PAGE

    with pytest.raises(HedronError) as mismatch:
        page.render("page.hdj", {}, mode=RenderMode.FRAGMENT)
    assert mismatch.value.diagnostic.code == "HED-JINJA-0020"

    library = HedronJinja(
        Environment(
            loader=DictLoader(
                {"macros.hdj": _hdj("{% macro x() %}x{% endmacro %}", kind="library")}
            )
        )
    )
    with pytest.raises(HedronError) as library_exc:
        library.render("macros.hdj", {})
    assert library_exc.value.diagnostic.code == "HED-JINJA-0020"

    malformed_page = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "bad.hdj": _hdj(
                        "<!DOCTYPE html><html><head></head><body>not closed",
                        kind="page",
                    )
                }
            )
        )
    )
    with pytest.raises(HedronError) as malformed_exc:
        malformed_page.render("bad.hdj", {})
    assert malformed_exc.value.diagnostic.code == "HED-JINJA-0017"

    closing_document_tag = HedronJinja(Environment(loader=DictLoader({"bad.hdj": _hdj("</body>")})))
    with pytest.raises(HedronError) as closing_exc:
        closing_document_tag.render("bad.hdj", {})
    assert closing_exc.value.diagnostic.code == "HED-JINJA-0017"


def test_template_spec_region_assertion_and_value_validation() -> None:
    source = _hdj('<section id="main">ok</section>', declarations='regions = ["main"]')
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))

    assert not templates.check(TemplateSpec("x.hdj", fragment_regions={"main": "#main"}))
    diagnostics = templates.check(TemplateSpec("x.hdj", fragment_regions={"other": "#other"}))
    assert diagnostics[0].code == "HED-JINJA-0020"

    with pytest.raises(ValueError, match="unique canonical"):
        TemplateSpec("x.hdj", assets=("app:main", "app:main"))


def test_static_dependency_graph_and_kind_matrix() -> None:
    loader = DictLoader(
        {
            "page.hdj": _hdj(
                '{% extends "base.hdj" %}{% block body %}{% include "part.hdj" %}{% endblock %}',
                kind="page",
            ),
            "base.hdj": _hdj(
                "<!DOCTYPE html><html><head></head><body>"
                "{% block body %}{% endblock %}</body></html>",
                kind="page",
            ),
            "part.hdj": _hdj("ok", kind="fragment"),
        }
    )
    templates = HedronJinja(Environment(loader=loader))

    assert not templates.check("page.hdj")
    assert templates.capabilities("page.hdj").dependencies == (
        "base.hdj",
        "part.hdj",
    )
    assert "ok" in templates.render("page.hdj", {}).html

    invalid_loader = DictLoader(
        {
            "page.hdj": _hdj('{% include "other.hdj" %}', kind="page"),
            "other.hdj": _hdj("bad", kind="page"),
        }
    )
    diagnostics = HedronJinja(Environment(loader=invalid_loader)).check("page.hdj")
    assert diagnostics[0].code == "HED-JINJA-0020"


def test_dynamic_and_foreign_dependencies_are_rejected_in_v1() -> None:
    dynamic = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj("{% include view.template %}")}))
    )
    assert dynamic.check("x.hdj")[0].code == "HED-JINJA-0022"

    foreign = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "x.hdj": _hdj('{% include "legacy.html" %}'),
                    "legacy.html": "legacy",
                }
            )
        )
    )
    assert foreign.check("x.hdj")[0].code == "HED-JINJA-0022"

    package = HedronJinja(Environment(loader=DictLoader({"pkg/x.hdj": _hdj("package")})))
    package_spec = TemplateSpec("pkg/x.hdj", source=TemplateSource.PACKAGE)
    assert package.check(package_spec)[0].code == "HED-JINJA-0002"


def test_profiles_are_allowances_not_unused_feature_claims() -> None:
    standard = HedronJinja(Environment(loader=DictLoader({"x.hdj": _hdj("plain")})))
    assert not standard.check("x.hdj")

    minimal_source = _hdj('{% include "part.hdj" %}', profile="minimal")
    minimal = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "x.hdj": minimal_source,
                    "part.hdj": _hdj("part", profile="minimal"),
                }
            )
        )
    )
    assert any(item.code == "HED-JINJA-0023" for item in minimal.check("x.hdj"))


def test_capability_declaration_and_policy_are_separate() -> None:
    body = "<style>body { color: red }</style>"
    under_declared = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj(body)})),
        allowed_capabilities={"browser.inline-style"},
    )
    assert any(item.code == "HED-JINJA-0024" for item in under_declared.check("x.hdj"))

    declared = _hdj(body, declarations='requires = ["browser.inline-style"]')
    policy_denied = HedronJinja(Environment(loader=DictLoader({"x.hdj": declared})))
    assert any(item.code == "HED-JINJA-0025" for item in policy_denied.check("x.hdj"))

    allowed = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": declared})),
        allowed_capabilities={"browser.inline-style"},
    )
    assert not allowed.check("x.hdj")


def test_static_page_assets_and_conditional_fragment_assets() -> None:
    asset = AssetRef(kind="script", href="/static/app.mjs")
    page_source = _hdj(
        "<!DOCTYPE html><html><head></head><body>ok</body></html>",
        kind="page",
        declarations='assets = ["app:main"]',
    )
    page = HedronJinja(
        Environment(loader=DictLoader({"page.hdj": page_source})),
        assets={"app:main": asset},
    )
    assert page.render("page.hdj", {}).assets == (asset,)

    conditional_page = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "page.hdj": _hdj(
                        "<!DOCTYPE html><html><head></head><body>"
                        '{% hedron_asset "app:main" %}</body></html>',
                        kind="page",
                    )
                }
            )
        ),
        assets={"app:main": asset},
    )
    assert any(item.code == "HED-JINJA-0019" for item in conditional_page.check("page.hdj"))

    page_with_fragment_asset = HedronJinja(
        Environment(
            loader=DictLoader(
                {
                    "page.hdj": _hdj(
                        "<!DOCTYPE html><html><head></head><body>"
                        '{% include "part.hdj" %}</body></html>',
                        kind="page",
                    ),
                    "part.hdj": _hdj("part", declarations='assets = ["app:main"]'),
                }
            )
        ),
        assets={"app:main": asset},
    )
    assert not page_with_fragment_asset.check("page.hdj")

    fragment_source = _hdj(
        '{% if view.load %}{% hedron_asset "app:main" %}{% endif %}',
        declarations='requires = ["browser.head-mutation"]',
    )
    fragment = HedronJinja(
        Environment(loader=DictLoader({"part.hdj": fragment_source})),
        assets={"app:main": asset},
        allowed_capabilities={"browser.head-mutation"},
    )
    assert fragment.render("part.hdj", {"load": True}).assets == (asset,)


def test_registered_remote_assets_use_purpose_specific_origin_capabilities() -> None:
    capability = "network.style-origin:https://cdn.example"
    source = _hdj(
        "<!DOCTYPE html><html><head>"
        '<link rel="stylesheet" href="{{ hdj.asset_url(\'vendor:theme\')|hedron_asset_url }}">'
        "</head><body>ok</body></html>",
        kind="page",
        declarations=(f'assets = ["vendor:theme"]\nrequires = ["{capability}"]'),
    )
    asset = AssetRef(kind="css", href="https://cdn.example/theme.css")
    templates = HedronJinja(
        Environment(loader=DictLoader({"page.hdj": source})),
        assets={"vendor:theme": asset},
        allowed_capabilities={capability},
    )

    assert templates.capabilities("page.hdj").inferred == frozenset({capability})
    result = templates.render("page.hdj", {})
    assert result.assets == (asset,)
    assert "https://cdn.example/theme.css" in result.html

    insecure = _hdj(
        "ok",
        declarations='requires = ["network.script-origin:http://cdn.example"]',
    )
    insecure_templates = HedronJinja(Environment(loader=DictLoader({"insecure.hdj": insecure})))
    assert insecure_templates.check("insecure.hdj")[0].code == "HED-JINJA-0018"

    with pytest.raises(HedronError) as insecure_asset:
        HedronJinja(
            Environment(loader=DictLoader({"x.hdj": _hdj("ok")})),
            assets={"vendor:script": AssetRef(kind="script", href="http://cdn.example/app.js")},
        )
    assert insecure_asset.value.diagnostic.code == "HED-JINJA-0019"

    with pytest.raises(HedronError) as unknown_kind:
        HedronJinja(
            Environment(loader=DictLoader({"x.hdj": _hdj("ok")})),
            assets={"vendor:data": AssetRef(kind="blob", href="https://cdn.example/data.bin")},
        )
    assert unknown_kind.value.diagnostic.code == "HED-JINJA-0019"


def test_asset_url_bridge_requires_static_declaration() -> None:
    asset = AssetRef(kind="image", href="/static/logo.svg")
    declared_source = _hdj(
        "<img src=\"{{ hdj.asset_url('app:logo')|hedron_asset_url }}\">",
        declarations=('assets = ["app:logo"]\nrequires = ["browser.head-mutation"]'),
    )
    declared = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": declared_source})),
        assets={"app:logo": asset},
        allowed_capabilities={"browser.head-mutation"},
    )
    assert declared.render("x.hdj", {}).assets == (asset,)

    undeclared_source = _hdj("<img src=\"{{ hdj.asset_url('app:logo')|hedron_asset_url }}\">")
    undeclared = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": undeclared_source})),
        assets={"app:logo": asset},
    )
    with pytest.raises(HedronError) as exc:
        undeclared.render("x.hdj", {})
    assert exc.value.diagnostic.code == "HED-JINJA-0019"


def test_environment_mutation_and_overlays_do_not_leak_binding() -> None:
    env = Environment(loader=DictLoader({"x.hdj": _hdj("ok")}))
    templates = HedronJinja(env)
    env.globals["late"] = object()
    with pytest.raises(HedronError) as changed:
        templates.check("x.hdj")
    assert changed.value.diagnostic.code == "HED-JINJA-0014"

    policy_env = Environment(loader=DictLoader({"x.hdj": _hdj("ok")}))
    policy_templates = HedronJinja(policy_env)
    policy_env.policies["json.dumps_kwargs"]["sort_keys"] = False
    with pytest.raises(HedronError) as policy_changed:
        policy_templates.check("x.hdj")
    assert policy_changed.value.diagnostic.code == "HED-JINJA-0014"

    base = Environment(loader=DictLoader({"x.hdj": _hdj("ok")}))
    HedronJinja(base)
    overlay = base.overlay()
    with pytest.raises(HedronError) as leaked:
        overlay.get_template("x.hdj").render()
    assert leaked.value.diagnostic.code == "HED-JINJA-0006"

    with pytest.raises(HedronError) as rebound:
        HedronJinja(overlay)
    assert rebound.value.diagnostic.code == "HED-JINJA-0014"
