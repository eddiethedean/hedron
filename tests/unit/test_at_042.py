"""AT-042: element inventory honesty (not SR-021 / #86)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core.plugins import PluginContext
from hedron_core.registry import reset_registry_for_tests
from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_data.editor import DataEditor
from hedron_data.plugin import PLUGIN_META as DATA_META
from hedron_data.plugin import register as register_data
from hedron_elements.action_async import ActionAsync
from hedron_elements.dialog import Dialog
from hedron_elements.field_text import FieldText
from hedron_elements.plugin import PLUGIN_META as ELEMENTS_META
from hedron_elements.plugin import register as register_elements

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "docs" / "acceptance" / "human-at" / "042" / "PROTOCOL.md"
DISPOSITION = ROOT / "docs" / "acceptance" / "human-at" / "042" / "DISPOSITION.toml"


def setup_function() -> None:
    reset_registry_for_tests()
    register_elements(PluginContext(ELEMENTS_META))
    register_data(PluginContext(DATA_META))


def teardown_function() -> None:
    reset_registry_for_tests()


def test_at_042_disclaims_product_wide_human_at() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    assert "SR-021" in protocol
    assert "#86" in protocol
    assert (
        "does **not** claim product-wide Supported human AT" in protocol
        or "does not claim product-wide Supported human AT" in protocol
    )
    data = tomllib.loads(DISPOSITION.read_text(encoding="utf-8"))
    assert data["gate"] == "AT-042"
    assert int(data["summary"]["blocking"]) == 0
    sessions = data.get("sessions") or []
    recorded = int(data["summary"]["sessions_recorded"])
    if data["state"] == "planned":
        assert recorded == 0
        assert sessions == []
    else:
        assert data["state"] == "verified"
        assert recorded >= 2
        # Disposition counters must match concrete session rows (not free-floating).
        assert len(sessions) == recorded
        for row in sessions:
            assert str(row.get("id", "")).startswith("AT-042-S")
            assert row.get("result") == "pass"
            assert row.get("matrix")
            assert row.get("surfaces")


def test_at_042_supported_workflows_keep_native_semantics() -> None:
    field = render(FieldText("email", value="a@b.c", label="Email")).html
    assert 'label="Email"' in field
    assert "<input" in field
    assert "hedron-field-text" in field
    dialog = render(Dialog(title="Settings")).html
    assert "hedron-dialog" in dialog
    editor = render(
        DataEditor(
            [{"id": "1", "n": "a"}],
            key_field="id",
            caption="Edit",
            save_endpoint="/s",
        )
    ).html
    assert "hedron-data-editor-fallback" in editor
    assert 'role="grid"' in editor
    action = render(
        ActionAsync(
            "Save",
            hx_post=SafeUrl.parse("/save", purpose=UrlPurpose.NAVIGATION),
        )
    ).html
    assert "hedron-action-async" in action
