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
from hedron_core.builtins import Checkbox, Expander, Select, TextArea, TextInput, ToggleSwitch
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


def test_hedron_ui_has_no_parallel_request_api_and_stays_single_source() -> None:
    core = Path("packages/hedron-core/src/hedron_core/static/hedron-ui.mjs")
    package = Path("packages/hedron/src/hedron/static/hedron-ui.mjs")

    assert "htmx.ajax" not in core.read_text(encoding="utf-8")
    assert core.read_bytes() == package.read_bytes()
