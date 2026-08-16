"""INTERACT-038 typed events and legacy mapping."""

from __future__ import annotations

from tests.unit.charts_038_helpers import sample_plan

from hedron_charts.assets_038 import chart_module_path
from hedron_charts.operators import EVENT_KINDS, LEGACY_EVENT_FAIL, LEGACY_EVENT_MAP


def test_event_kinds_locked() -> None:
    assert {
        "inspect",
        "focus",
        "select",
        "legend_filter",
        "brush",
        "zoom",
        "pan",
        "reset",
        "crosshair",
        "drill_intent",
    } == EVENT_KINDS


def test_legacy_event_mapping() -> None:
    assert LEGACY_EVENT_MAP["hover"] == "inspect"
    assert LEGACY_EVENT_MAP["click"] == "select"
    assert "extend" in LEGACY_EVENT_FAIL


def test_plan_interaction_flags() -> None:
    plan = sample_plan()
    assert plan.interaction.inspect is True
    assert plan.interaction.focus_navigation is True


def test_element_emits_versioned_event_names() -> None:
    src = chart_module_path().read_text(encoding="utf-8")
    for kind in ("inspect", "focus", "select", "reset"):
        assert "hedron-chart-" in src
        assert f'"{kind}"' in src or f"'{kind}'" in src or f'emit(el, "{kind}"' in src


def test_keydown_listener_removed_on_cleanup() -> None:
    """#270: remounts must not stack keydown listeners."""
    src = chart_module_path().read_text(encoding="utf-8")
    assert 'removeEventListener("keydown"' in src
    assert "_hedronChartKeydown" in src
    assert "dropKeydown" in src
