"""PLUGIN-031 coverage for sample-kit discovery and disable/uninstall semantics."""

from __future__ import annotations

from hedron_core.plugins import PluginContext, reset_explorer_panels_for_tests
from hedron_sample_kit.plugin import PLUGIN_META, register


def test_sample_kit_registers_explorer_panel() -> None:
    reset_explorer_panels_for_tests()
    ctx = PluginContext(PLUGIN_META)
    register(ctx)
    assert PLUGIN_META.name == "sample_kit"
    assert PLUGIN_META.capabilities.explorer_panels is True


def test_sample_kit_meta_pins_living_train() -> None:
    # Compatibility floor for the exemplar plugin.
    assert "0.33" in PLUGIN_META.hedron_version
