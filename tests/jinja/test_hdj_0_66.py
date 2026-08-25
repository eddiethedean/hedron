"""Phase 0.66 app-scoped HDJ registry and context parity."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Annotated, cast

import pytest
from jinja2 import DictLoader, Environment
from pydantic import BaseModel
from tests.unit._helpers_045 import make_app, reset_045

from hedron import FormBody, Text
from hedron_core import (
    AssetRef,
    HedronError,
    HtmxContext,
    RenderContext,
    RenderMode,
    RenderResult,
)
from hedron_core.registry import register_application_style, register_asset, register_theme
from hedron_jinja import (
    HdjContext,
    HedronJinja,
    JinjaBinding,
    ProviderManifest,
    charts_provider_manifest,
    data_provider_manifest,
    elements_provider_manifest,
    extras_provider_manifest,
    maps_provider_manifest,
)


def setup_function() -> None:
    reset_045()


def _hdj(body: str, *, features: tuple[str, ...] = ()) -> str:
    feature_line = f"features = {list(features)!r}\n".replace("'", '"') if features else ""
    return (
        f'---hdj\nversion = 1\nkind = "fragment"\nprofile = "standard"\n{feature_line}---\n{body}'
    )


def _result_trace(result: RenderResult) -> Mapping[str, object]:
    assert result.trace is not None
    return cast(Mapping[str, object], result.trace)


def test_app_bound_logical_id_renders_live_view() -> None:
    app = make_app()

    @app.refreshable("/items/{item_id}")
    def item(item_id: str):
        return Text(f"Item {item_id}")

    binding = JinjaBinding(
        app_id=app.hedron_app_id,
        handles={item.logical_id: item},
    )
    templates = HedronJinja(
        Environment(
            loader=DictLoader(
                {"x.hdj": _hdj(f'{{{{ h_view("{item.logical_id}", item_id="n1") }}}}')}
            )
        ),
        binding=binding,
    )

    result = templates.render("x.hdj", {})
    trace = _result_trace(result)

    assert "Item n1" in result.html
    assert item.path.split("{")[0] in result.html
    assert trace["app_id"] == app.hedron_app_id
    assert trace["binding_fingerprint"] == binding.fingerprint
    assert cast(int, trace["node_count"]) >= 1
    assert len(cast(tuple[object, ...], trace["components"])) == 1


def test_app_bound_parameterless_view_is_materialized() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("Ready")

    binding = JinjaBinding(app_id=app.hedron_app_id, handles={status.logical_id: status})
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj(f'{{{{ h_view("{status.logical_id}") }}}}')})),
        binding=binding,
    )

    result = templates.render("x.hdj", {})

    assert "Ready" in result.html


def test_app_bound_command_form_and_type_schema() -> None:
    app = make_app()

    class Payload(BaseModel):
        title: str = "hi"

    @app.command(fallback="/")
    def add(data: Annotated[Payload, FormBody()]):
        return Text(data.title)

    binding = JinjaBinding(app_id=app.hedron_app_id, handles={add.logical_id: add})
    body = (
        f'{{{{ h_command_form("{add.logical_id}") }}}}'
        f'{{{{ h_type_schema("{add.logical_id}")["schema_version"] }}}}'
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj(body, features=("hedron.type-schema",))})),
        binding=binding,
    )

    result = templates.render("x.hdj", {})

    assert "<form" in result.html
    schema = binding.type_schema(add.logical_id)
    assert schema is not None
    assert str(schema["schema_version"]) in result.html


def test_binding_rejects_cross_app_live_handle() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    with pytest.raises(ValueError, match="belongs to app"):
        JinjaBinding(app_id="another-app", handles={status.logical_id: status})


def test_binding_fingerprint_covers_asset_contract() -> None:
    first = JinjaBinding(
        app_id="app-066",
        assets={"application:css": AssetRef(kind="css", href="/static/a.css")},
    )
    second = JinjaBinding(
        app_id="app-066",
        assets={"application:css": AssetRef(kind="css", href="/static/b.css")},
    )

    assert first.fingerprint != second.fingerprint


def test_binding_is_snapshot_immutable_and_fingerprint_is_order_independent() -> None:
    first_assets = {
        "application:css": AssetRef(kind="css", href="/static/app.css"),
        "application:logo": AssetRef(kind="image", href="/static/logo.svg"),
    }
    first = JinjaBinding(
        app_id=" app-066 ",
        assets=first_assets,
        providers={"hedron.maps": maps_provider_manifest()},
        themes=("ops", "night", "ops"),
    )
    second = JinjaBinding(
        app_id="app-066",
        assets=dict(reversed(tuple(first_assets.items()))),
        providers={"hedron.maps": maps_provider_manifest()},
        themes=("ops", "night"),
    )

    first_assets.clear()

    assert first.app_id == "app-066"
    assert first.themes == ("ops", "night")
    assert set(first.assets) == {"application:css", "application:logo"}
    assert first.fingerprint == second.fingerprint
    with pytest.raises(TypeError):
        first.assets["late"] = AssetRef(kind="css", href="/late.css")  # type: ignore[index]


def test_binding_fingerprint_covers_provider_manifest() -> None:
    manifest = maps_provider_manifest()
    changed = ProviderManifest(
        feature_id=manifest.feature_id,
        package=manifest.package,
        version=f"{manifest.version}+changed",
        assets=manifest.assets,
        capabilities=manifest.capabilities,
    )

    first = JinjaBinding(app_id="app-066", providers={manifest.feature_id: manifest})
    second = JinjaBinding(app_id="app-066", providers={changed.feature_id: changed})

    assert first.fingerprint != second.fingerprint


def test_binding_rejects_mismatched_handle_and_provider_keys() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    with pytest.raises(ValueError, match="does not match logical_id"):
        JinjaBinding(app_id=app.hedron_app_id, handles={"wrong": status})

    manifest = maps_provider_manifest()
    with pytest.raises(ValueError, match="does not match feature_id"):
        JinjaBinding(app_id=app.hedron_app_id, providers={"hedron.data": manifest})


def test_environment_rejects_app_id_that_disagrees_with_binding() -> None:
    binding = JinjaBinding(app_id="app-066")

    with pytest.raises(ValueError, match="must match"):
        HedronJinja(
            Environment(loader=DictLoader({"x.hdj": _hdj("ok")})),
            binding=binding,
            app_id="another-app",
        )


def test_registry_projection_exposes_redacted_styles_themes_assets_and_provider(
    tmp_path: Path,
) -> None:
    stylesheet = tmp_path / "app.css"
    stylesheet.write_text(".app { color: var(--hedron-color-text); }", encoding="utf-8")
    register_application_style(
        name="app",
        source=stylesheet,
        scope="app",
        allowed_roots=(tmp_path,),
    )
    register_theme(logical_id="theme:ops", name="ops", tokens={"color.text": "#111111"})
    register_asset(
        logical_id="application:css",
        kind="css",
        path="/static/application.css",
        digest="sha256-test",
        content_type="text/css",
    )
    binding = JinjaBinding.from_registry(
        app_id="app-066",
        import_registered_components=False,
        asset_hrefs={"application:css": "/static/application.css"},
        providers=(maps_provider_manifest(),),
    )
    source = _hdj(
        "{{ hdj.app_id }}|{{ hdj.themes[0] }}|"
        "{{ hdj.application_styles[0].scope }}|{{ hdj.has_provider('hedron.maps') }}",
        features=("hedron.application-styles", "hedron.maps"),
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source})),
        binding=binding,
    )

    result = templates.render("x.hdj", {})

    assert result.html == "app-066|ops|app|True"
    assert "application:css" in templates.assets
    assert binding.application_styles[0].digest.startswith("sha256-")
    style_fact = binding.application_styles[0].as_mapping()
    assert set(style_fact) == {
        "logical_id",
        "name",
        "owner",
        "scope",
        "layer",
        "global",
        "media",
        "digest",
        "provenance",
    }
    assert str(stylesheet) not in json.dumps(style_fact, sort_keys=True)
    assert str(tmp_path) not in result.html


def test_registry_asset_source_path_is_not_projected_without_public_href(
    tmp_path: Path,
) -> None:
    source_asset = tmp_path / "private.css"
    source_asset.write_text(".private {}", encoding="utf-8")
    register_asset(
        logical_id="application:private-css",
        kind="css",
        path=str(source_asset),
        digest="sha256-test",
        content_type="text/css",
    )

    binding = JinjaBinding.from_registry(
        app_id="app-066",
        import_registered_components=False,
    )

    assert "application:private-css" not in binding.assets


def test_registry_projection_rejects_unknown_public_asset_id() -> None:
    with pytest.raises(ValueError, match="absent from the registry"):
        JinjaBinding.from_registry(
            app_id="app-066",
            import_registered_components=False,
            asset_hrefs={"missing:asset": "/static/missing.css"},
        )


def test_registered_handle_must_be_explicitly_present_in_binding() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj(f'{{{{ h_view("{status.logical_id}") }}}}')})),
        binding=JinjaBinding(app_id=app.hedron_app_id),
    )

    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", {})

    assert exc.value.diagnostic.title == "HDJ live handle is not bound"


def test_app_bound_helper_refuses_manifest_dictionary_execution() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("ok")

    binding = JinjaBinding(app_id=app.hedron_app_id, handles={status.logical_id: status})
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj("{{ h_view(view.target) }}")})),
        binding=binding,
    )

    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", {"target": binding.catalog_facts(status.logical_id)})

    assert exc.value.diagnostic.title == "Manifest dictionaries are not executable in templates"


def test_app_bound_view_requires_all_binding_parameters() -> None:
    app = make_app()

    @app.refreshable("/items/{item_id}")
    def item(item_id: str):
        return Text(item_id)

    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": _hdj(f'{{{{ h_view("{item.logical_id}") }}}}')})),
        binding=JinjaBinding(app_id=app.hedron_app_id, handles={item.logical_id: item}),
    )

    with pytest.raises(HedronError) as exc:
        templates.render("x.hdj", {})

    assert (
        exc.value.diagnostic.title == "Jinja view helper requires a FragmentHandle or BoundFragment"
    )


def test_htmx_request_facts_are_explicit_and_immutable() -> None:
    source = _hdj("{{ hdj.htmx.target }}|{{ hdj.htmx.boosted }}")
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))
    request = HtmxContext(is_htmx=True, target="results", boosted=True)

    result = templates.render(
        "x.hdj",
        {},
        context=RenderContext.standalone(theme="aurora"),
        htmx=request,
    )
    trace = _result_trace(result)
    trace_htmx = cast(Mapping[str, object], trace["htmx"])

    assert result.html == "results|True"
    assert trace["theme"] == "aurora"
    assert trace_htmx["target"] == "results"

    facade = HdjContext(
        mode=result.mode,
        locale="en",
        theme=None,
        htmx={"extras": {"request_id": "r1"}},
    )
    with pytest.raises(TypeError):
        facade.htmx["extras"]["request_id"] = "changed"  # type: ignore[index]


@pytest.mark.parametrize(
    ("facts", "message"),
    [
        ({str(index): index for index in range(33)}, "at most 32"),
        ({"": "value"}, "non-empty string keys"),
        ({"value": "x" * 4097}, "at most 4096"),
        ({"value": list(range(33))}, "at most 32 values"),
        ({"a": {"b": {"c": {"d": {"e": "too deep"}}}}}, "at most four levels"),
    ],
)
def test_htmx_request_fact_budgets_are_enforced(
    facts: dict[str, object],
    message: str,
) -> None:
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": _hdj("{{ hdj.htmx }}")})))

    with pytest.raises(ValueError, match=message):
        templates.render("x.hdj", {}, htmx=facts)  # type: ignore[arg-type]


def test_htmx_request_facts_reject_non_json_values() -> None:
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": _hdj("{{ hdj.htmx }}")})))

    with pytest.raises(TypeError, match="JSON-compatible"):
        templates.render("x.hdj", {}, htmx={"bad": {"not-json"}})  # type: ignore[dict-item]


def test_hdj_context_deep_freezes_provider_and_style_facts() -> None:
    providers: dict[str, dict[str, object]] = {
        "hedron.maps": {
            "feature_id": "hedron.maps",
            "capabilities": ["map", "layers"],
        }
    }
    styles: tuple[dict[str, object], ...] = (
        {"logical_id": "application:css", "media": ["screen"]},
    )
    facade = HdjContext(
        mode=RenderMode.FRAGMENT,
        locale="en",
        theme=None,
        providers=providers,
        application_styles=styles,
    )

    cast(list[str], providers["hedron.maps"]["capabilities"]).append("changed")
    cast(list[str], styles[0]["media"]).append("print")

    assert facade.providers["hedron.maps"]["capabilities"] == ("map", "layers")
    assert facade.application_styles[0]["media"] == ("screen",)
    with pytest.raises(TypeError):
        facade.providers["hedron.maps"]["feature_id"] = "changed"  # type: ignore[index]


def test_all_first_party_provider_manifests_are_canonical_and_unique() -> None:
    manifests = (
        data_provider_manifest(),
        charts_provider_manifest(),
        maps_provider_manifest(),
        elements_provider_manifest(),
        extras_provider_manifest(),
    )

    assert {manifest.feature_id for manifest in manifests} == {
        "hedron.data",
        "hedron.charts",
        "hedron.maps",
        "hedron.elements",
        "hedron.extras",
    }
    for manifest in manifests:
        assert manifest.package
        assert manifest.version
        assert len(manifest.assets) == len(set(manifest.assets))
        assert len(manifest.capabilities) == len(set(manifest.capabilities))


def test_declared_provider_must_be_present_in_app_binding() -> None:
    source = _hdj(
        '{{ hdj.has_provider("hedron.maps") }}',
        features=("hedron.maps",),
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source})),
        binding=JinjaBinding(app_id="app-066"),
    )

    diagnostics = templates.check("x.hdj")

    assert any(
        item.code == "HED-JINJA-0023" and "hedron.maps" in item.explanation for item in diagnostics
    )


@pytest.mark.anyio
async def test_app_bound_view_has_sync_async_render_parity() -> None:
    app = make_app()

    @app.refreshable
    def status():
        return Text("Ready")

    binding = JinjaBinding(app_id=app.hedron_app_id, handles={status.logical_id: status})
    source = _hdj(
        f'{{{{ h_view("{status.logical_id}") }}}}',
        features=("jinja.async",),
    )
    templates = HedronJinja(
        Environment(loader=DictLoader({"x.hdj": source}), enable_async=True),
        binding=binding,
    )

    result = await templates.render_async("x.hdj", {})
    trace = _result_trace(result)

    assert "Ready" in result.html
    assert trace["app_id"] == app.hedron_app_id
    assert trace["binding_fingerprint"] == binding.fingerprint


def test_custom_profile_detects_new_bound_helpers() -> None:
    source = (
        '---hdj\nversion = 1\nkind = "fragment"\nprofile = "custom"\n---\n'
        '{{ h_type_schema("status") }}{{ h_feature_bundles() }}'
    )
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))

    diagnostics = templates.check("x.hdj")

    explanations = " ".join(item.explanation for item in diagnostics)
    assert "hedron.type-schema" in explanations
    assert "hedron.feature-bundles" in explanations


def test_custom_profile_detects_catalog_facts_as_interaction() -> None:
    source = (
        '---hdj\nversion = 1\nkind = "fragment"\nprofile = "custom"\n---\n'
        '{{ h_catalog_facts("status") }}'
    )
    templates = HedronJinja(Environment(loader=DictLoader({"x.hdj": source})))

    diagnostics = templates.check("x.hdj")

    assert any("hedron.interaction" in item.explanation for item in diagnostics)
