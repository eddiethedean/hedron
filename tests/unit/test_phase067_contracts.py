"""Executable evidence for the Phase 0.67 typed browser contract."""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from hedron.responses import render_component_response
from hedron_core import (
    AlpineAttrs,
    AlpineExpression,
    AlpineFeatureDemand,
    BrowserFeaturePlan,
    BrowserPlanClosure,
    FutureWarningRecord,
    FutureWarningRegistry,
    HedronFutureWarning,
    Interaction,
    Outcome,
    emit_future_warning,
)
from hedron_core.browser_assets_067 import ALPINE_067_ARTIFACTS, alpine_artifact_manifest
from hedron_core.diagnostics import HedronError
from hedron_core.html import html
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import RenderMode, render


def test_typed_alpine_attributes_are_collected_and_assets_are_demand_driven() -> None:
    attrs = AlpineAttrs(
        state={"open": False},
        directives={
            "x-on:click": AlpineExpression.assign("open", AlpineExpression.literal(True)),
            "x-show": AlpineExpression.name("open"),
        },
        source="test:disclosure",
    )
    result = render(html.div("content", alpine=attrs), mode=RenderMode.PAGE)

    assert result.browser_plan.requires("data")
    assert result.browser_plan.requires("on")
    assert result.browser_plan.requires("show")
    assert "/hedron-static/alpine/csp-3.16.3.js" in result.browser_plan.assets
    assert "/hedron-static/hedron-alpine.mjs" in result.browser_plan.assets
    page = inject_page_assets(result.html, result.mode, browser_plan=result.browser_plan)
    assert page.count("hedron-alpine.mjs") == 1
    assert result.browser_plan.fingerprint in page

    feature_off = render(html.div("content"), mode=RenderMode.PAGE)
    plain = inject_page_assets(
        feature_off.html, feature_off.mode, browser_plan=feature_off.browser_plan
    )
    assert feature_off.browser_plan.feature_off
    assert "hedron-alpine.mjs" not in plain
    assert "hedron-browser-plan" not in plain

    focus = render(
        html.div("dialog", alpine=AlpineAttrs(state={"open": True}, features=("focus",))),
        mode=RenderMode.PAGE,
    )
    assert "/hedron-static/alpine/focus-3.16.3.js" in focus.browser_plan.assets


def test_raw_alpine_markup_and_illegal_interactions_fail_closed() -> None:
    with pytest.raises(HedronError) as raw:
        html.button("bad", **{"x-on:click": "open = true"})
    assert raw.value.diagnostic.code == "HED-SEC-0014"

    with pytest.raises(ValueError):
        AlpineAttrs(directives={"x-on:click": "open = true"})
    with pytest.raises(ValueError):
        AlpineAttrs(directives={"x-init": "fetch"})
    with pytest.raises((TypeError, ValueError)):
        Interaction("local", request_effect=object())  # type: ignore[arg-type]


def test_browser_plan_closure_is_immutable_and_fragment_subset_is_proven() -> None:
    initial = BrowserFeaturePlan.from_demands((AlpineFeatureDemand("data", "page"),))
    fragment = BrowserFeaturePlan.from_demands((AlpineFeatureDemand("data", "fragment"),))
    closure = BrowserPlanClosure(initial=initial).add_fragment("panel", fragment)
    assert closure.fragment("panel") == fragment
    assert closure.document_plan.requires("data")
    assert closure.fingerprint == closure.document_plan.fingerprint
    with pytest.raises(ValueError, match="missing_features"):
        closure.assert_fragment_subset(
            BrowserFeaturePlan.from_demands((AlpineFeatureDemand("focus", "late"),))
        )


def test_render_response_uses_page_closure_and_rejects_late_fragment_requirements() -> None:
    closure = BrowserPlanClosure(
        initial=BrowserFeaturePlan.from_demands((AlpineFeatureDemand("data", "page"),))
    )
    page = render_component_response(
        render(html.div("page"), mode=RenderMode.PAGE), browser_closure=closure
    )
    assert "hedron-browser-plan" in page.body.decode()
    with pytest.raises(Exception, match="HED-BROWSER-0671|browser feature plan"):
        render_component_response(
            render(
                html.div(
                    "fragment",
                    alpine=AlpineAttrs(state={"open": False}, features=("focus",), source="late"),
                ),
                mode=RenderMode.FRAGMENT,
            ),
            browser_closure=closure,
        )


def test_phase067_supply_catalog_has_exact_csp_and_nine_official_plugins() -> None:
    assert set(ALPINE_067_ARTIFACTS) == {
        "core",
        "anchor",
        "collapse",
        "focus",
        "intersect",
        "mask",
        "morph",
        "persist",
        "resize",
        "sort",
        "ui",
    }
    assert all(
        item.version == "3.16.3" and item.license == "MIT" for item in ALPINE_067_ARTIFACTS.values()
    )
    assert len(alpine_artifact_manifest()) == 11


def test_interaction_and_outcome_are_closed_and_serializable() -> None:
    local = Interaction.local("toggle", state_keys=("open",))
    combined = Interaction.combined("toggle", "save", target="#panel")
    assert local.to_attributes()["data-hedron-state-keys"] == "open"
    assert local.demands()[0].feature == "interaction"
    assert combined.to_dict()["kind"] == "combined"
    assert Outcome.validation({"name": "required"}).to_dict()["role"] == "validation"
    assert Outcome.refresh("orders").to_dict()["payload"] == {"handles": ["orders"]}


def test_future_warning_registry_is_structured_and_visible() -> None:
    record = FutureWarningRecord(
        code="HED-MIGRATE-0670",
        old_path="app.fragment",
        replacement="app.view",
        owner="hedron",
        source="test.py:1",
        documentation="docs/implementation/HEDRON_1_0_EDRON_INTERFACE_AUDIT.md",
        fixture="tests/upgrade/shared.py",
        automation_status="automatic",
    )
    registry = FutureWarningRegistry((record,))
    assert registry.get(record.code) is record
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        emit_future_warning(record)
    assert caught and isinstance(caught[0].message, HedronFutureWarning)
    assert caught[0].message.record is record  # type: ignore[attr-defined]


def test_alpine_runtime_is_local_and_csp_safe() -> None:
    source = Path("packages/hedron-core/src/hedron_core/static/hedron-alpine.mjs").read_text(
        encoding="utf-8"
    )
    assert "unsafe-eval" not in source
    assert "eval(" not in source
    assert "fetch(" not in source
    assert "htmx.ajax" not in source
