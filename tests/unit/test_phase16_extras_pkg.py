"""Phase 0.16 extras package and FeatureManifest isolation."""

from __future__ import annotations

from hedron_core.plugin_loader import load_plugins
from hedron_core.plugins import (
    get_explorer_panels,
    get_feature_manifests,
    reset_explorer_panels_for_tests,
)
from hedron_core.registry import get_registry, reset_registry_for_tests
from hedron_extras.plugin import register as extras_register


class _EP:
    def __init__(self, name: str = "hedron_extras") -> None:
        self.name = name

    def load(self) -> object:
        return extras_register


def setup_function() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()


def test_feature_manifest_registration() -> None:
    loader = load_plugins(
        enabled=["hedron_extras"],
        hedron_version="0.22.0",
        entry_points=[_EP()],
    )
    assert any(p.meta.name == "hedron_extras" for p in loader.loaded)
    features = get_feature_manifests(plugin="hedron_extras")
    names = {f.name for f in features}
    assert "composition" in names
    assert "workbench" in names
    assert "terminal" in names
    assert "recipes" in names
    terminal = next(f for f in features if f.name == "terminal")
    assert terminal.stability == "experimental"
    workbench = next(f for f in features if f.name == "workbench")
    assert any(a.startswith("hedron-extras:") for a in workbench.assets)


def test_extras_components_registered() -> None:
    load_plugins(
        enabled=["hedron_extras"],
        hedron_version="0.22.0",
        entry_points=[_EP()],
    )
    registry = get_registry()
    names = {meta.name for meta in registry.components()}
    assert "CodeEditor" in names
    assert "TreeView" in names
    assert "TerminalView" in names
    code = next(m for m in registry.components() if m.name == "CodeEditor")
    assert code.browser_modules
    assets = {a.logical_id: a for a in registry.assets()}
    editor_asset = assets["hedron-extras:assets.code_editor.editor.js"]
    assert editor_asset.kind == "module"
    assert editor_asset.attributes.get("type") == "module"
    modules = list(registry.browser_modules())
    assert any(m.tag_name == "hedron-extras-code-editor" for m in modules)
    extras_panel = next(p for p in get_explorer_panels() if p.panel_id == "hedron-extras-features")
    assert extras_panel.path == "/hedron-explorer/packages"


def test_core_import_isolation_without_extras_assets() -> None:
    """Importing core alone must not register extras assets."""
    import hedron_core  # noqa: F401

    asset_ids = {a.logical_id for a in get_registry().assets()}
    assert not any(aid.startswith("hedron-extras:") for aid in asset_ids)
