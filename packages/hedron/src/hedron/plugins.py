"""Plugin discovery — re-exported from hedron-core for compatibility."""

from hedron_core.plugin_loader import (
    ENTRY_POINT_GROUP,
    LoadedPlugin,
    PluginLoader,
    compatible_hedron_version,
    load_plugins,
)

__all__ = [
    "ENTRY_POINT_GROUP",
    "LoadedPlugin",
    "PluginLoader",
    "compatible_hedron_version",
    "load_plugins",
]
