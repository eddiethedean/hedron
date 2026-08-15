"""Explorer panel, feature, and diagnostic-owner registrations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from hedron_core.plugins.meta import StabilityLabel

__all__ = [
    "ExplorerPanelMeta",
    "FeatureManifest",
    "get_diagnostic_owners",
    "get_explorer_panels",
    "get_feature_manifests",
    "register_diagnostic_owner",
    "register_explorer_panel",
    "register_feature",
    "reset_explorer_panels_for_tests",
    "reset_feature_manifests_for_tests",
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


_panels: dict[str, ExplorerPanelMeta] = {}
_diagnostic_owners: dict[str, str] = {}
_features: dict[str, FeatureManifest] = {}


def register_feature(manifest: FeatureManifest) -> None:
    key = f"{manifest.plugin}:{manifest.name}"
    # Allow re-registration so nested FastAPI lifespans / test reloads can reload plugins.
    _features[key] = manifest


def get_feature_manifests(*, plugin: str | None = None) -> tuple[FeatureManifest, ...]:
    items: Sequence[FeatureManifest] = tuple(_features.values())
    if plugin is not None:
        items = tuple(f for f in items if f.plugin == plugin)
    return tuple(sorted(items, key=lambda f: (f.plugin, f.name)))


def reset_feature_manifests_for_tests() -> None:
    _features.clear()


def register_explorer_panel(
    *,
    panel_id: str,
    title: str,
    plugin: str,
    description: str = "",
    path: str = "",
) -> None:
    if panel_id in _panels:
        from hedron_core.codes import HED_PLUGIN_DUPLICATE
        from hedron_core.diagnostics import error

        raise error(
            HED_PLUGIN_DUPLICATE,
            title="Duplicate Explorer panel",
            explanation=f"Panel {panel_id!r} is already registered.",
            remediation="Use a unique panel_id per plugin contribution.",
        )
    _panels[panel_id] = ExplorerPanelMeta(
        panel_id=panel_id,
        title=title,
        plugin=plugin,
        description=description,
        path=path,
    )


def get_explorer_panels() -> tuple[ExplorerPanelMeta, ...]:
    return tuple(sorted(_panels.values(), key=lambda p: p.panel_id))


def register_diagnostic_owner(code_prefix: str, owner: str) -> None:
    _diagnostic_owners[code_prefix] = owner


def get_diagnostic_owners() -> Mapping[str, str]:
    return dict(_diagnostic_owners)


def reset_explorer_panels_for_tests() -> None:
    _panels.clear()
    _diagnostic_owners.clear()
    _features.clear()
