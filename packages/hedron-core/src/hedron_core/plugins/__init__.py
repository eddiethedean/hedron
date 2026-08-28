"""Plugin metadata and Explorer extension contracts (framework-neutral)."""

from __future__ import annotations

from hedron_core.plugins.context import PluginContext
from hedron_core.plugins.definition import (
    CallbackContribution,
    PluginContribution,
    PluginDefinition,
)
from hedron_core.plugins.explorer import (
    ExplorerPanelMeta,
    ExplorerProvider,
    FeatureManifest,
    get_explorer_panels,
    get_explorer_providers,
    get_feature_manifests,
    register_explorer_panel,
    register_explorer_provider,
    register_feature,
    reset_explorer_panels_for_tests,
    reset_feature_manifests_for_tests,
)
from hedron_core.plugins.explorer import (
    _diagnostic_owners as _diagnostic_owners,
)
from hedron_core.plugins.explorer import (
    _features as _features,
)
from hedron_core.plugins.explorer import (
    _panels as _panels,
)
from hedron_core.plugins.explorer import (
    get_diagnostic_owners as get_diagnostic_owners,
)
from hedron_core.plugins.explorer import (
    register_diagnostic_owner as register_diagnostic_owner,
)
from hedron_core.plugins.meta import PluginCapabilities, PluginMeta
from hedron_core.plugins.meta import StabilityLabel as StabilityLabel

__all__ = [
    "ExplorerPanelMeta",
    "ExplorerProvider",
    "FeatureManifest",
    "PluginCapabilities",
    "PluginMeta",
    "PluginContext",
    "CallbackContribution",
    "PluginContribution",
    "PluginDefinition",
    "get_explorer_panels",
    "get_explorer_providers",
    "get_feature_manifests",
    "register_explorer_panel",
    "register_explorer_provider",
    "register_feature",
    "reset_explorer_panels_for_tests",
    "reset_feature_manifests_for_tests",
]
