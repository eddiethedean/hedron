"""PERF-042: inventory budget locks plus Supported render bounds.

Measured render/payload budgets live in ``tests/performance/test_budgets.py``
(bound into PERF-042 via ``GATE_TESTS``). This module locks the inventory
ceilings and a coarse SSR markup sanity bound — not a substitute for Lighthouse
or real browser interaction timing.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core.plugins import PluginContext
from hedron_core.registry import reset_registry_for_tests
from hedron_core.rendering import render
from hedron_data.editor import DataEditor
from hedron_data.plugin import PLUGIN_META
from hedron_data.plugin import register as register_data
from hedron_elements.example import Example
from hedron_elements.plugin import PLUGIN_META as ELEMENTS_META
from hedron_elements.plugin import register as register_elements

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "acceptance" / "supported-element-inventory-042.toml"


def setup_function() -> None:
    reset_registry_for_tests()
    register_elements(PluginContext(ELEMENTS_META))
    register_data(PluginContext(PLUGIN_META))


def teardown_function() -> None:
    reset_registry_for_tests()


def test_perf_042_named_budget_ceilings_locked() -> None:
    """Inventory ceiling values are the locked contract (exact), not self-inequalities."""
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    budgets = data["budgets"]
    assert budgets["reference_app"] == "examples/reference-app"
    assert int(budgets["bundle_kb_ceiling"]) == 750
    assert int(budgets["request_count_ceiling"]) == 40
    assert int(budgets["upgrade_ms_ceiling"]) == 2500
    assert int(budgets["interaction_ms_ceiling"]) == 100
    assert int(budgets["memory_mb_ceiling"]) == 256
    assert int(budgets["leak_listeners_ceiling"]) == 0
    assert float(budgets["layout_shift_ceiling"]) == 0.1
    assert (ROOT / "examples" / "reference-app").is_dir()
    assert (ROOT / "tests" / "performance" / "test_budgets.py").is_file()


def test_perf_042_supported_surfaces_render_within_markup_bound() -> None:
    rows = [{"id": str(i), "name": f"r{i}"} for i in range(40)]
    editor = render(DataEditor(rows, key_field="id", save_endpoint="/s")).html
    assert "hedron-data-editor" in editor
    # Coarse SSR bound (not the 750KB *bundle* ceiling).
    assert len(editor.encode("utf-8")) < 200_000
    example = render(Example(status="ok")).html
    assert "hedron-example" in example
    assert len(example.encode("utf-8")) < 50_000
