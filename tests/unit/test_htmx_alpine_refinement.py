"""Regression coverage for the HTMX/Alpine refinement contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

from hedron_core import (
    AlpineExpression,
    HtmxAttrs,
    Interaction,
    html,
    render,
)
from hedron_core.builtins import Checkbox, Expander, Select, Tabs, TextArea, TextInput, ToggleSwitch
from hedron_core.page_assets import inject_page_assets
from hedron_core.rendering import RenderMode


def test_unary_expression_is_typed_and_csp_safe() -> None:
    expression = AlpineExpression.not_(AlpineExpression.name("open"))

    assert expression.to_source() == "!open"
    assert expression.to_dict() == {
        "kind": "unary",
        "value": "!",
        "args": [{"kind": "name", "value": "open"}],
    }


def test_explicit_interaction_state_creates_a_self_contained_scope() -> None:
    interaction = Interaction.local(
        "toggle",
        state_keys=("open",),
        state={"open": False},
    )
    rendered = render(html.button("Toggle", interaction=interaction)).html

    assert 'x-data="{&quot;open&quot;:false}"' in rendered
    assert 'x-on:click="open = !open"' in rendered
    assert 'data-hedron-local-scope="self"' in rendered


def test_interaction_lowering_uses_the_generic_htmx_builder() -> None:
    interaction = Interaction.request("save", target="#panel", sync="this:drop")
    lowered = interaction.to_lowering()

    assert lowered.alpine is None
    assert lowered.htmx is None  # no registry route exists in this isolated test
    assert lowered.to_attributes()["data-hedron-handle"] == "save"


def test_generic_htmx_builder_validates_and_emits_any_element_request() -> None:
    attrs = HtmxAttrs(
        method="get",
        url="/orders",
        target="#orders",
        swap="innerHTML",
        trigger="change from:#filter",
        sync="closest form:drop",
    ).as_html_attrs()

    assert str(attrs["hx-get"]) == "/orders"
    assert attrs["hx-target"] == "#orders"
    assert attrs["hx-trigger"] == "change from:#filter"
    assert attrs["hx-sync"] == "closest form:drop"

    with pytest.raises(ValueError):
        HtmxAttrs(method="get", url="/orders", sync="this:unknown").as_html_attrs()


def test_htmx_builder_composes_headers_without_changing_swap() -> None:
    attrs = HtmxAttrs(swap="none").merge(HtmxAttrs(headers='{"X-CSRF-Token":"token"}'))

    assert attrs.as_html_attrs() == {
        "hx-swap": "none",
        "hx-headers": '{"X-CSRF-Token":"token"}',
    }


def test_htmx_builder_keeps_legacy_default_and_tracks_explicit_omission() -> None:
    assert HtmxAttrs().as_html_attrs() == {"hx-swap": "outerHTML"}
    assert HtmxAttrs(swap=None).as_html_attrs() == {}
    assert HtmxAttrs().merge(HtmxAttrs(swap="innerHTML")).as_html_attrs() == {
        "hx-swap": "innerHTML"
    }
    assert HtmxAttrs(swap=None).merge(HtmxAttrs()).as_html_attrs() == {}


def test_htmx_bridge_is_loaded_for_htmx_without_widget_runtime() -> None:
    request = render(
        html.button(
            "Refresh",
            **HtmxAttrs(method="get", url="/refresh", target="#panel").as_html_attrs(),
        ),
        mode=RenderMode.PAGE,
    )
    page = inject_page_assets(
        request.html,
        request.mode,
        browser_plan=request.browser_plan,
        demand_driven=True,
    )

    assert "hedron-htmx.mjs" in page
    assert "hedron-ui.mjs" not in page


def test_demand_driven_page_assets_leave_native_pages_without_optional_runtime() -> None:
    native = render(html.main("Native content"), mode=RenderMode.PAGE)
    assert native.requires_htmx is False
    native_page = inject_page_assets(
        native.html,
        native.mode,
        browser_plan=native.browser_plan,
        demand_driven=True,
    )

    assert "htmx.min.js" not in native_page
    assert "hedron-ui.mjs" not in native_page
    assert "hedron-disclose.mjs" not in native_page

    request = render(
        html.button(
            "Refresh",
            **HtmxAttrs(method="get", url="/refresh", target="#panel").as_html_attrs(),
        ),
        mode=RenderMode.PAGE,
    )
    assert request.requires_htmx is True
    request_page = inject_page_assets(
        request.html,
        request.mode,
        browser_plan=request.browser_plan,
        demand_driven=True,
    )
    assert "htmx.min.js" in request_page


@pytest.mark.parametrize(
    "control",
    [
        TextInput("name", enhance="native"),
        TextArea("bio", enhance="native"),
        Select("role", (("admin", "Admin"),), enhance="native"),
        Checkbox("enabled", "Enabled", enhance="native"),
        ToggleSwitch("enabled", "Enabled", enhance="native"),
    ],
)
def test_native_control_mode_does_not_request_alpine(control: object) -> None:
    result = render(control)  # type: ignore[arg-type]

    assert "x-model" not in result.html
    assert "x-data" not in result.html
    assert result.browser_plan.feature_off


def test_expander_native_mode_uses_details_without_alpine_or_collapse() -> None:
    result = render(Expander("More", "Details", enhance="native"))

    assert "<details" in result.html
    assert "x-data" not in result.html
    assert "x-collapse" not in result.html
    assert result.browser_plan.feature_off


def test_tabs_have_one_owner_and_no_js_safe_initial_panel_state() -> None:
    result = render(Tabs(("Overview", "one"), ("History", "two")))

    assert "x-data" not in result.html
    assert result.html.count('role="tabpanel"') == 2
    assert 'role="tabpanel" hidden' not in result.html


def test_ownerless_local_interaction_synthesizes_a_real_scope() -> None:
    interaction = Interaction.local("toggle")
    rendered = render(html.button("Toggle", interaction=interaction)).html

    assert interaction.local_effect is not None
    assert interaction.local_effect.state_keys == ("toggle",)
    assert dict(interaction.local_effect.state or {}) == {"toggle": False}
    assert 'x-data="{&quot;toggle&quot;:false}"' in rendered
    assert 'x-on:click="toggle = !toggle"' in rendered


def test_legacy_ownerless_state_keys_receive_false_defaults() -> None:
    interaction = Interaction.local("toggle", state_keys=("open",))

    assert interaction.local_effect is not None
    assert dict(interaction.local_effect.state or {}) == {"open": False}


def test_self_owned_state_without_keys_uses_the_action_as_its_key() -> None:
    interaction = Interaction.local("toggle", state={"toggle": True})
    rendered = render(html.button("Toggle", interaction=interaction)).html

    assert interaction.local_effect is not None
    assert interaction.local_effect.state_keys == ("toggle",)
    assert 'x-on:click="toggle = !toggle"' in rendered


def test_document_busy_bridge_retains_markers_until_host_is_idle() -> None:
    bridge = Path("packages/hedron-core/src/hedron_core/static/hedron-htmx.mjs").read_text(
        encoding="utf-8"
    )

    assert "if (!on) markersByHost.delete(host);" in bridge
    assert "record.host !== document.documentElement" in bridge


def test_hedron_ui_has_no_parallel_request_api_and_stays_single_source() -> None:
    core = Path("packages/hedron-core/src/hedron_core/static/hedron-ui.mjs")
    package = Path("packages/hedron/src/hedron/static/hedron-ui.mjs")

    assert "htmx.ajax" not in core.read_text(encoding="utf-8")
    assert core.read_bytes() == package.read_bytes()

    bridge = Path("packages/hedron-core/src/hedron_core/static/hedron-htmx.mjs")
    bridge_package = Path("packages/hedron/src/hedron/static/hedron-htmx.mjs")
    assert "htmx.ajax" not in bridge.read_text(encoding="utf-8")
    assert bridge.read_bytes() == bridge_package.read_bytes()
