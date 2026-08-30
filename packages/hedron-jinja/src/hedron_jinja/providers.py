"""HDJ provider manifests for hedron.data / hedron.charts parity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from importlib import import_module, metadata

from hedron_core.typing_aliases import JsonObject

_FEATURE_RE = re.compile(r"^[a-z][a-z0-9-]*(?:\.[a-z][a-z0-9-]*)+$")


@dataclass(frozen=True, slots=True)
class ProviderManifest:
    feature_id: str
    package: str
    version: str
    assets: tuple[str, ...]
    capabilities: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _FEATURE_RE.fullmatch(self.feature_id):
            raise ValueError("provider feature_id must be a dotted canonical ID")
        if not self.package.strip() or not self.version.strip():
            raise ValueError("provider package and version must be non-empty")
        assets = tuple(self.assets)
        capabilities = tuple(self.capabilities)
        if any(
            not isinstance(item, str)  # pyright: ignore[reportUnnecessaryIsInstance]
            or not item.strip()
            for item in (*assets, *capabilities)
        ):
            raise ValueError("provider assets and capabilities must be non-empty strings")
        if len(assets) != len(set(assets)) or len(capabilities) != len(set(capabilities)):
            raise ValueError("provider assets and capabilities must be unique")
        object.__setattr__(self, "assets", assets)
        object.__setattr__(self, "capabilities", capabilities)

    def as_mapping(self) -> JsonObject:
        return {
            "feature_id": self.feature_id,
            "package": self.package,
            "version": self.version,
            "assets": list(self.assets),
            "capabilities": list(self.capabilities),
        }


def _pkg_version(dist: str) -> str:
    try:
        return metadata.version(dist)
    except metadata.PackageNotFoundError:
        return "missing"


def data_provider_manifest() -> ProviderManifest:
    return ProviderManifest(
        feature_id="hedron.data",
        package="hedron-data",
        version=_pkg_version("hedron-data"),
        assets=("hedron-data:tabulator", "hedron-data:aggrid"),
        capabilities=(
            "datatable",
            "dataeditor",
            "transform-plan",
            "saved-views",
            "bounded-sources",
        ),
    )


def charts_provider_manifest() -> ProviderManifest:
    return ProviderManifest(
        feature_id="hedron.charts",
        package="hedron-charts",
        version=_pkg_version("hedron-charts"),
        assets=("hedron-charts:plotly-host", "hedron-charts:vega-host"),
        capabilities=(
            "beginner-charts",
            "typed-events",
            "annotations",
            "optional-adapters",
            "runtime-pins",
        ),
    )


def maps_provider_manifest() -> ProviderManifest:
    return ProviderManifest(
        feature_id="hedron.maps",
        package="hedron-maps",
        version=_pkg_version("hedron-maps"),
        assets=(
            "hedron-maps:hedron-map.mjs",
            "hedron-maps:hedron-map.css",
            "hedron-maps:maplibre.runtime.js",
            "hedron-maps:maplibre.css",
        ),
        capabilities=("map", "layers", "markers", "typed-events", "offline-fallback"),
    )


def elements_provider_manifest() -> ProviderManifest:
    return ProviderManifest(
        feature_id="hedron.elements",
        package="hedron-elements",
        version=_pkg_version("hedron-elements"),
        assets=("hedron-elements:bridge.mjs", "hedron-elements:interaction-state.mjs"),
        capabilities=("custom-elements", "form-associated", "native-fallback", "typed-events"),
    )


def extras_provider_manifest() -> ProviderManifest:
    return ProviderManifest(
        feature_id="hedron.extras",
        package="hedron-extras",
        version=_pkg_version("hedron-extras"),
        assets=(),
        capabilities=("curated-components", "workbenches", "explicit-trust"),
    )


def provider_available(feature_id: str) -> bool:
    mapping = {
        "hedron.data": "hedron_data",
        "hedron.charts": "hedron_charts",
        "hedron.maps": "hedron_maps",
        "hedron.elements": "hedron_elements",
        "hedron.extras": "hedron_extras",
    }
    module = mapping.get(feature_id)
    if module is None:
        return False
    try:
        import_module(module)
    except ImportError:
        return False
    return True


__all__ = [
    "ProviderManifest",
    "charts_provider_manifest",
    "data_provider_manifest",
    "elements_provider_manifest",
    "extras_provider_manifest",
    "maps_provider_manifest",
    "provider_available",
]
