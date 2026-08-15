"""Intelligent Auto() renderer registry and bounded Data Intelligence."""

from __future__ import annotations

from hedron_core.auto.factories import register_defaults
from hedron_core.auto.inspect import inspect_data
from hedron_core.auto.registry import (
    clear_renderers_for_tests,
    list_renderers,
    register_renderer,
)
from hedron_core.auto.registry import (
    get_last_auto_decision as get_last_auto_decision,
)
from hedron_core.auto.spec import AutoDecision, DataIntelligenceReport, RendererSpec
from hedron_core.auto.widget import Auto

__all__ = [
    "Auto",
    "AutoDecision",
    "DataIntelligenceReport",
    "RendererSpec",
    "clear_renderers_for_tests",
    "inspect_data",
    "list_renderers",
    "register_renderer",
]

register_defaults()
