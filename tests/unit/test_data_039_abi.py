"""DATA-039 / OPTIMISTIC-039 / CHARTLINK-039 unit evidence."""

from __future__ import annotations

import pytest

from hedron_core.cross_filter import (
    CHART_038_EVENT_KINDS,
    compose_chartlink_039,
    triggers_from_hedron_chart_event,
)
from hedron_core.dashboard import InteractionGraph
from hedron_core.plugins import PluginContext
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.rendering import render
from hedron_data.editor import ABI_VERSION, ELEMENT_ID, TAG_NAME, DataEditor
from hedron_data.optimistic import (
    DENY_BY_DEFAULT_RISKS,
    OptimisticMutation,
    OptimisticMutationState,
    OptimisticPatch,
    assert_optimism_allowed,
)
from hedron_data.plugin import PLUGIN_META
from hedron_data.plugin import register as register_data


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    reset_registry_for_tests()
    yield
    reset_registry_for_tests()


@pytest.fixture()
def data_plugin() -> None:
    register_data(PluginContext(PLUGIN_META))


def test_data_editor_renders_abi_custom_element(data_plugin) -> None:
    markup = render(
        DataEditor(
            [{"id": "1", "name": "Ada"}],
            key_field="id",
            caption="People",
            save_endpoint="/save",
        )
    ).html
    assert f"<{TAG_NAME}" in markup
    assert f'data-hedron-abi="{ABI_VERSION}"' in markup
    assert f'data-hedron-element="{ELEMENT_ID}"' in markup
    assert "hedron-data-editor-fallback" in markup
    assert "data-hedron-payload" in markup
    assert 'data-hedron-server-region="fallback"' in markup


def test_data_editor_element_definition_registered(data_plugin) -> None:
    meta = get_registry().get_element_definition("hedron-data-editor")
    assert meta is not None
    assert meta.abi_version == 1
    assert meta.tag_name == TAG_NAME
    assert "hedron-data-cell-edit" in meta.events
    assert "hedron-data-optimistic" in meta.events
    assert meta.lifecycle.get("disconnect") == "abort+dispose"
    assert meta.fallback.get("table") == "semantic"


def test_optimistic_mutation_state_machine() -> None:
    mut = OptimisticMutation.from_cell_edits(
        action_id="dataeditor.save",
        base_revision="3",
        patches=[OptimisticPatch(row_key="1", field="name", value="Ada", previous="A")],
        allowed_fields=frozenset({"name"}),
    )
    assert mut.state is OptimisticMutationState.CANONICAL
    mut.propose().submit().confirm(server_revision="4")
    assert mut.state is OptimisticMutationState.CONFIRMED
    assert mut.base_revision == "4"


def test_optimistic_mutation_conflict_refetch() -> None:
    mut = OptimisticMutation.from_cell_edits(
        action_id="dataeditor.save",
        base_revision="1",
        patches=[{"row_key": "1", "field": "name", "value": "x"}],
        allowed_fields=frozenset({"name"}),
    )
    mut.propose().submit().conflict().resolve_with_refetch(server_revision="9")
    assert mut.state is OptimisticMutationState.REFETCHED
    assert mut.base_revision == "9"


@pytest.mark.parametrize("risk", sorted(DENY_BY_DEFAULT_RISKS))
def test_optimistic_deny_by_default(risk: str) -> None:
    with pytest.raises(ValueError, match="deny-by-default"):
        assert_optimism_allowed(risk)


def test_optimistic_rejects_html_patch() -> None:
    with pytest.raises(ValueError, match="HTML"):
        OptimisticMutation.from_cell_edits(
            action_id="dataeditor.save",
            base_revision="1",
            patches=[OptimisticPatch(row_key="1", field="name", value="<script>")],
            allowed_fields=frozenset({"name"}),
        )


def test_chartlink_039_binds_published_chart_events() -> None:
    graph = InteractionGraph()
    binding = compose_chartlink_039(graph, targets=("grid-region", "chart-region"))
    assert "grid.selection" in binding.triggers
    assert "chart.select" in binding.triggers
    assert "chart.legend_filter" in binding.triggers
    assert "chart.brush" in binding.triggers
    for kind in ("select", "legend_filter", "brush"):
        assert kind in CHART_038_EVENT_KINDS
        assert triggers_from_hedron_chart_event(kind)


def test_chartlink_rejects_unknown_kind() -> None:
    with pytest.raises(ValueError, match="Unknown"):
        triggers_from_hedron_chart_event("plotly_click")
