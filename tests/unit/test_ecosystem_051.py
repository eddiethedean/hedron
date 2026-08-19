"""ECOSYSTEM-051 extras projections."""

from __future__ import annotations

from hedron_core import __version__ as core_version
from hedron_core.plugin_loader import load_plugins
from hedron_core.plugins import get_explorer_panels, reset_explorer_panels_for_tests
from hedron_core.registry import reset_registry_for_tests
from hedron_extras.descriptor import extras_features
from hedron_extras.plugin import register as extras_register


class _EP:
    name = "hedron_extras"

    def load(self) -> object:
        return extras_register


def setup_function() -> None:
    reset_registry_for_tests()
    reset_explorer_panels_for_tests()


def test_explorer_and_projection_fields() -> None:
    load_plugins(enabled=["hedron_extras"], hedron_version=core_version, entry_points=[_EP()])
    panel = next(p for p in get_explorer_panels() if p.panel_id == "hedron-extras-features")
    assert panel.path == "/hedron-explorer/packages"
    for feature in extras_features():
        assert feature.explorer_projection
        assert feature.jinja_projection
        assert feature.conformance_projection
