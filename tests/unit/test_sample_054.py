"""SAMPLE-054 evidence: modular sample-kit variants and the shared fixture."""

from __future__ import annotations

import tomllib
from collections.abc import Iterator
from pathlib import Path

import pytest

from hedron.testing import render_html
from hedron_conformance.authoring_loop import (
    AUTHORING_LOOP_SCHEMA_VERSION,
    AuthoringLoopFixture,
    validate_fixture_schema,
)
from hedron_core import get_registry, reset_bundles_for_tests, reset_registry_for_tests
from hedron_core.bundles import included_bundles
from hedron_core.plugins import PluginContext
from hedron_sample_kit import authoring_fixture, list_variants
from hedron_sample_kit.plugin import PLUGIN_META, register
from hedron_sample_kit.variants import (
    VARIANT_MODULES,
    hdj,
    iter_variants,
    load_variant,
    optional,
    web_component,
    workflow,
)


@pytest.fixture
def registered() -> Iterator[None]:
    reset_registry_for_tests()
    reset_bundles_for_tests()
    register(PluginContext(PLUGIN_META))
    yield
    reset_registry_for_tests()
    reset_bundles_for_tests()


def test_sample_054_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.54.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["SAMPLE-054"]["owner"] == "hedron-sample-kit"
    assert Path("docs/rfcs/RFC-0081-AUTHORING-LOOP-AND-CHROME.md").is_file()


def test_variants_are_listed_and_independently_loadable() -> None:
    assert list_variants() == VARIANT_MODULES
    for module in iter_variants():
        assert module.VARIANT_ID in VARIANT_MODULES
        assert callable(module.register)


def test_missing_variant_folder_is_skipped_not_fatal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deleting a variant folder must not break the rest of the kit."""
    import hedron_sample_kit.variants as variants

    assert load_variant("no_such_variant") is None
    monkeypatch.setattr(variants, "VARIANT_MODULES", ("workflow", "no_such_variant"))
    assert variants.list_variants() == ("workflow",)


def test_web_component_variant_keeps_ssr_fallback(registered: None) -> None:
    registry = get_registry()
    element = registry.get_element_definition(web_component.ELEMENT_ID)
    assert element is not None
    assert element.tag_name == web_component.TAG_NAME
    assert element.fallback["js_off"] == web_component.SSR_FALLBACK_TEXT
    asset_ids = {asset.logical_id for asset in registry.assets()}
    assert web_component.MODULE_ASSET_ID in asset_ids
    assert web_component.STYLES_ASSET_ID in asset_ids
    html = render_html(web_component.WebCallout(message="fallback stays visible"))
    assert web_component.TAG_NAME in html
    assert "fallback stays visible" in html


def test_workflow_variant_projects_typed_actions(registered: None) -> None:
    bundles = {bundle.logical_id: bundle for bundle in included_bundles()}
    bundle = bundles[workflow.BUNDLE_ID]
    projection = bundle.projections[0]
    assert projection.namespace == workflow.NAMESPACE
    action_ids = [str(row["action_id"]) for row in projection.data["actions"]]
    assert action_ids == [action.action_id for action in workflow.actions()]
    assert [str(row["step_id"]) for row in projection.data["steps"]] == ["draft", "publish"]
    assert workflow.PublishNoteInput().audience == "team"


def test_hdj_variant_registers_binding_marker_only(registered: None) -> None:
    assert hdj.binding_marker_present()
    asset_ids = {asset.logical_id for asset in get_registry().assets()}
    assert hdj.TEMPLATE_ASSET_ID in asset_ids
    bundle = {b.logical_id: b for b in included_bundles()}[hdj.BUNDLE_ID]
    assert bundle.optional_capabilities == ("hdj-render",)
    assert any("hedron-jinja" in text for text in bundle.projections[0].limitations)


def test_optional_variant_reports_missing_extra_honestly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(optional.ENV_FLAG, raising=False)
    status = optional.optional_status()
    assert status["active"] is False
    assert status["reason"]
    bundle = optional.feature_bundle("0.1.10")
    capability = bundle.projections[0].capabilities[0]
    assert capability.support == "unavailable"
    assert capability.limitation == status["reason"]

    monkeypatch.setenv(optional.ENV_FLAG, "1")
    assert optional.optional_status()["env_enabled"] is True


def test_authoring_fixture_uses_the_shared_schema() -> None:
    fixture = authoring_fixture()
    assert fixture.schema_version == AUTHORING_LOOP_SCHEMA_VERSION
    assert fixture.kind == "authoring_loop_fixture"
    assert fixture.payload["variants"] == list(list_variants())
    payload = fixture.to_dict()
    assert validate_fixture_schema(payload) == []
    assert AuthoringLoopFixture.from_dict(payload) == fixture
