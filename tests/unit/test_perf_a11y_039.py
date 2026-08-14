"""PERF-039 / A11Y-039 evidence (scoped)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core.plugins import PluginContext
from hedron_core.registry import reset_registry_for_tests
from hedron_core.rendering import render
from hedron_data.editor import DataEditor
from hedron_data.plugin import PLUGIN_META
from hedron_data.plugin import register as register_data
from hedron_data.table import DataTable

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "acceptance" / "rich-surface-inventory-039.toml"
AT_DISPOSITION = ROOT / "docs" / "acceptance" / "human-at" / "039" / "DISPOSITION.toml"
AT_PROTOCOL = ROOT / "docs" / "acceptance" / "human-at" / "039" / "PROTOCOL.md"


def setup_function() -> None:
    reset_registry_for_tests()
    register_data(PluginContext(PLUGIN_META))


def teardown_function() -> None:
    reset_registry_for_tests()


def test_perf_039_named_budgets_locked() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    budgets = data["budgets"]
    assert budgets["named_large_scenarios"] == "required"
    assert budgets["rich_adapters_default"] is False
    assert budgets["rich_adapters_transitive"] is False


def test_perf_039_large_editor_render_bound() -> None:
    rows = [{"id": str(i), "name": f"r{i}"} for i in range(80)]
    html = render(DataEditor(rows, key_field="id", save_endpoint="/s")).html
    assert "hedron-data-editor" in html
    assert html.count("<tr") >= 1  # fallback rows present


def test_a11y_039_fallback_and_scoped_protocol() -> None:
    table = render(DataTable([{"id": "1", "n": "a"}], caption="People")).html
    assert "<table" in table
    assert "People" in table
    protocol = AT_PROTOCOL.read_text(encoding="utf-8")
    assert "does not claim Supported human AT" in protocol
    assert "SR-021" in protocol
    disp = tomllib.loads(AT_DISPOSITION.read_text(encoding="utf-8"))
    assert disp["gate"] == "A11Y-039"
    editor = render(
        DataEditor([{"id": "1", "n": "a"}], key_field="id", caption="Edit", save_endpoint="/s")
    ).html
    assert "hedron-data-editor-fallback" in editor
    assert 'role="grid"' in editor
