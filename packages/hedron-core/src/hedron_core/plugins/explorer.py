"""Explorer panel, feature, and diagnostic-owner registrations."""

from __future__ import annotations

from collections.abc import Callable, Generator, Mapping, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field

from hedron_core.plugins.meta import StabilityLabel

__all__ = [
    "ExplorerPanelMeta",
    "ExplorerProvider",
    "FeatureManifest",
    "PluginRegistryState",
    "get_diagnostic_owners",
    "get_explorer_panels",
    "get_explorer_providers",
    "get_feature_manifests",
    "new_plugin_registry",
    "register_diagnostic_owner",
    "register_explorer_panel",
    "register_explorer_provider",
    "register_feature",
    "restore_plugin_state",
    "snapshot_plugin_state",
    "reset_explorer_panels_for_tests",
    "reset_feature_manifests_for_tests",
    "use_plugin_registry",
]


@dataclass(frozen=True, slots=True)
class FeatureManifest:
    """Per-feature capability manifest for curated extras (phase 0.16)."""

    name: str
    plugin: str
    stability: StabilityLabel = "beta"
    dependencies: tuple[str, ...] = ()
    assets: tuple[str, ...] = ()
    a11y_notes: str = ""
    security_notes: str = ""
    http_fallback: bool = True
    description: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "plugin": self.plugin,
            "stability": self.stability,
            "dependencies": list(self.dependencies),
            "assets": list(self.assets),
            "a11y_notes": self.a11y_notes,
            "security_notes": self.security_notes,
            "http_fallback": self.http_fallback,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class ExplorerPanelMeta:
    panel_id: str
    title: str
    plugin: str
    description: str = ""
    path: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "panel_id": self.panel_id,
            "title": self.title,
            "plugin": self.plugin,
            "description": self.description,
            "path": self.path,
        }


@dataclass(frozen=True, slots=True)
class ExplorerProvider:
    """Additive Explorer panel provider (0.50). Does not replace ExplorerPanelMeta."""

    panel_id: str
    title: str
    plugin: str
    description: str = ""
    path: str = ""
    capabilities: tuple[str, ...] = ()
    timeout_ms: int = 250
    max_payload_bytes: int = 65_536
    ordering: int = 0
    redaction_profile: str = "standard"
    render: Callable[[], object] | None = None

    def to_panel_meta(self) -> ExplorerPanelMeta:
        return ExplorerPanelMeta(
            panel_id=self.panel_id,
            title=self.title,
            plugin=self.plugin,
            description=self.description,
            path=self.path,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "panel_id": self.panel_id,
            "title": self.title,
            "plugin": self.plugin,
            "description": self.description,
            "path": self.path,
            "capabilities": list(self.capabilities),
            "timeout_ms": self.timeout_ms,
            "max_payload_bytes": self.max_payload_bytes,
            "ordering": self.ordering,
            "redaction_profile": self.redaction_profile,
        }


@dataclass(slots=True)
class PluginRegistryState:
    """Application-owned plugin contributions.

    Plugin entry points are discovered process-wide, but their registrations
    must not leak between applications sharing one interpreter.
    """

    panels: dict[str, ExplorerPanelMeta] = field(default_factory=dict[str, ExplorerPanelMeta])
    providers: dict[str, ExplorerProvider] = field(default_factory=dict[str, ExplorerProvider])
    diagnostic_owners: dict[str, str] = field(default_factory=dict[str, str])
    features: dict[str, FeatureManifest] = field(default_factory=dict[str, FeatureManifest])


_panels: dict[str, ExplorerPanelMeta] = {}
_providers: dict[str, ExplorerProvider] = {}
_diagnostic_owners: dict[str, str] = {}
_features: dict[str, FeatureManifest] = {}

_default_state = PluginRegistryState(
    panels=_panels,
    providers=_providers,
    diagnostic_owners=_diagnostic_owners,
    features=_features,
)
_scoped_state: ContextVar[PluginRegistryState | None] = ContextVar(
    "hedron_plugin_registry", default=None
)


def _active_state() -> PluginRegistryState:
    return _scoped_state.get() or _default_state


def new_plugin_registry() -> PluginRegistryState:
    """Create application state seeded from legacy process registrations."""
    return PluginRegistryState(
        panels=dict(_default_state.panels),
        providers=dict(_default_state.providers),
        diagnostic_owners=dict(_default_state.diagnostic_owners),
        features=dict(_default_state.features),
    )


@contextmanager
def use_plugin_registry(state: PluginRegistryState) -> Generator[None, None, None]:
    """Bind plugin contributions to one application/task context."""
    token = _scoped_state.set(state)
    try:
        yield
    finally:
        _scoped_state.reset(token)


def snapshot_plugin_state() -> dict[str, dict[str, object]]:
    """Capture the active plugin registries for transactional loading."""
    state = _active_state()
    return {
        "panels": dict(state.panels),
        "providers": dict(state.providers),
        "diagnostic_owners": dict(state.diagnostic_owners),
        "features": dict(state.features),
    }


def restore_plugin_state(snapshot: Mapping[str, Mapping[str, object]]) -> None:
    """Restore a snapshot made by :func:`snapshot_plugin_state`."""
    state = _active_state()
    state.panels.clear()
    state.panels.update(snapshot["panels"])  # type: ignore[arg-type]
    state.providers.clear()
    state.providers.update(snapshot["providers"])  # type: ignore[arg-type]
    state.diagnostic_owners.clear()
    state.diagnostic_owners.update(snapshot["diagnostic_owners"])  # type: ignore[arg-type]
    state.features.clear()
    state.features.update(snapshot["features"])  # type: ignore[arg-type]


# Mutable registries are exposed only for the package compatibility façade and
# transactional plugin-loader snapshots.
panels_registry = _panels
diagnostic_owners_registry = _diagnostic_owners
features_registry = _features


def register_feature(manifest: FeatureManifest) -> None:
    key = f"{manifest.plugin}:{manifest.name}"
    # Allow re-registration so nested FastAPI lifespans / test reloads can reload plugins.
    _active_state().features[key] = manifest


def get_feature_manifests(*, plugin: str | None = None) -> tuple[FeatureManifest, ...]:
    items: Sequence[FeatureManifest] = tuple(_active_state().features.values())
    if plugin is not None:
        items = tuple(f for f in items if f.plugin == plugin)
    return tuple(sorted(items, key=lambda f: (f.plugin, f.name)))


def reset_feature_manifests_for_tests() -> None:
    _active_state().features.clear()


def register_explorer_panel(
    *,
    panel_id: str,
    title: str,
    plugin: str,
    description: str = "",
    path: str = "",
) -> None:
    state = _active_state()
    if panel_id in state.panels:
        from hedron_core.codes import HED_PLUGIN_DUPLICATE
        from hedron_core.diagnostics import error

        raise error(
            HED_PLUGIN_DUPLICATE,
            title="Duplicate Explorer panel",
            explanation=f"Panel {panel_id!r} is already registered.",
            remediation="Use a unique panel_id per plugin contribution.",
        )
    state.panels[panel_id] = ExplorerPanelMeta(
        panel_id=panel_id,
        title=title,
        plugin=plugin,
        description=description,
        path=path,
    )


def get_explorer_panels() -> tuple[ExplorerPanelMeta, ...]:
    return tuple(sorted(_active_state().panels.values(), key=lambda p: p.panel_id))


def register_explorer_provider(provider: ExplorerProvider) -> None:
    """Register an additive provider and upsert matching ExplorerPanelMeta."""
    state = _active_state()
    existing = state.providers.get(provider.panel_id)
    if existing is not None and existing != provider:
        from hedron_core.codes import HED_PLUGIN_DUPLICATE
        from hedron_core.diagnostics import error

        raise error(
            HED_PLUGIN_DUPLICATE,
            title="Duplicate Explorer provider",
            explanation=f"Provider {provider.panel_id!r} is already registered.",
            remediation="Use a unique panel_id per plugin contribution.",
        )
    state.providers[provider.panel_id] = provider
    if provider.panel_id not in state.panels:
        register_explorer_panel(
            panel_id=provider.panel_id,
            title=provider.title,
            plugin=provider.plugin,
            description=provider.description,
            path=provider.path,
        )


def get_explorer_providers() -> tuple[ExplorerProvider, ...]:
    return tuple(sorted(_active_state().providers.values(), key=lambda p: (p.ordering, p.panel_id)))


def register_diagnostic_owner(code_prefix: str, owner: str) -> None:
    _active_state().diagnostic_owners[code_prefix] = owner


def get_diagnostic_owners() -> Mapping[str, str]:
    return dict(_active_state().diagnostic_owners)


def reset_explorer_panels_for_tests() -> None:
    state = _active_state()
    state.panels.clear()
    state.providers.clear()
    state.diagnostic_owners.clear()
    state.features.clear()
