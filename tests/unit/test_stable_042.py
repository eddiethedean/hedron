"""STABLE-042: Supported element inventory honesty for locked D-070 tags."""

from __future__ import annotations

import tomllib
from pathlib import Path

from hedron_core.plugins import PluginContext
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_core.rendering import render
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_data.editor import DataEditor
from hedron_data.plugin import PLUGIN_META as DATA_META
from hedron_data.plugin import register as register_data
from hedron_elements.action_async import ActionAsync
from hedron_elements.dialog import Dialog
from hedron_elements.disclosure import Disclosure
from hedron_elements.example import Example
from hedron_elements.field_choice import FieldChoice
from hedron_elements.field_file import FieldFile
from hedron_elements.field_text import FieldText
from hedron_elements.plugin import PLUGIN_META as ELEMENTS_META
from hedron_elements.plugin import register as register_elements

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "docs" / "acceptance" / "supported-element-inventory-042.toml"
STATIC = ROOT / "packages" / "hedron-elements" / "src" / "hedron_elements" / "static"
DATA_EDITOR_JS = (
    ROOT / "packages" / "hedron-data" / "src" / "hedron_data" / "assets" / "tabulator" / "editor.js"
)

LOCKED = (
    "hedron-example",
    "hedron-field-text",
    "hedron-field-choice",
    "hedron-field-file",
    "hedron-disclosure",
    "hedron-dialog",
    "hedron-action-async",
    "hedron-data-editor",
)


def setup_function() -> None:
    reset_registry_for_tests()
    register_elements(PluginContext(ELEMENTS_META))
    register_data(PluginContext(DATA_META))


def teardown_function() -> None:
    reset_registry_for_tests()


def test_inventory_locks_eight_tags_and_contracts() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    assert tuple(data["supported_tags"]) == LOCKED
    assert data["element_state_ownership"]["supported"] == [
        "controlled",
        "local",
        "draft",
        "preference",
    ]
    assert "ambient_global_store" in data["element_state_ownership"]["excluded"]
    assert data["react_migration_bridge"]["in_hedron_elements"] is False
    assert data["npm_mirror"]["react_runtime"] is False
    for tag in LOCKED:
        row = data["tags"][tag]
        assert row["abi_version"] >= 1
        assert row["ssr_fallback"]
        assert row["package"] in {"hedron-elements", "hedron-data"}


def test_supported_element_modules_exist() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    for tag in LOCKED:
        row = data["tags"][tag]
        if row["package"] == "hedron-elements":
            assert (STATIC / row["module"]).is_file(), tag
        else:
            assert DATA_EDITOR_JS.is_file()


def test_supported_tags_render_with_abi_and_fallback() -> None:
    cases = [
        (Example(), "hedron-example", None),
        (FieldText("n"), "hedron-field-text", None),
        (FieldChoice("c", (("a", "A"),)), "hedron-field-choice", None),
        (FieldFile(name="f"), "hedron-field-file", None),
        (Disclosure(summary="Title"), "hedron-disclosure", None),
        (Dialog(title="Dlg"), "hedron-dialog", None),
        (
            ActionAsync(
                "Go",
                hx_post=SafeUrl.parse("/go", purpose=UrlPurpose.NAVIGATION),
            ),
            "hedron-action-async",
            None,
        ),
        (
            DataEditor(
                [{"id": "1", "n": "a"}],
                key_field="id",
                save_endpoint="/s",
            ),
            "hedron-data-editor",
            "hedron-data-editor-fallback",
        ),
    ]
    for component, tag, fallback in cases:
        html = render(component).html
        assert f"<{tag}" in html
        assert "data-hedron-abi=" in html
        if fallback:
            assert fallback in html
    registry = get_registry()
    for tag in LOCKED:
        assert registry.get_element_definition(tag) is not None  # type: ignore[attr-defined]


def test_experimental_exclusions_remain_named() -> None:
    data = tomllib.loads(INVENTORY.read_text(encoding="utf-8"))
    excluded = data["experimental_or_excluded"]
    assert "sse" in excluded["live_transports"]
    assert "spa_framework_claim" in excluded["other"]
    assert "CodeEditor" in excluded["specialty_ui"]
