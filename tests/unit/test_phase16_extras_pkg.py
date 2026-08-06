"""Phase 0.16 extras package and FeatureManifest isolation."""

from __future__ import annotations

from hedron_core.plugin_loader import load_plugins
from hedron_core.plugins import get_feature_manifests, reset_explorer_panels_for_tests
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
        hedron_version="0.16.0",
        entry_points=[_EP()],
    )
    assert any(p.meta.name == "hedron_extras" for p in loader.loaded)
    features = get_feature_manifests(plugin="hedron_extras")
    names = {f.name for f in features}
    assert "composition" in names
    assert "workbench" in names
    assert "terminal" in names
    terminal = next(f for f in features if f.name == "terminal")
    assert terminal.stability == "experimental"


def test_extras_components_registered() -> None:
    load_plugins(
        enabled=["hedron_extras"],
        hedron_version="0.16.0",
        entry_points=[_EP()],
    )
    names = {meta.name for meta in get_registry().components()}
    assert "CodeEditor" in names
    assert "TreeView" in names
    assert "TerminalView" in names


def test_core_import_isolation_without_extras_assets() -> None:
    """Importing core alone must not register extras assets."""
    import hedron_core  # noqa: F401

    asset_ids = {a.logical_id for a in get_registry().assets()}
    assert not any(aid.startswith("hedron-extras:") for aid in asset_ids)
