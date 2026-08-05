"""HDJ provider manifests for hedron.data / hedron.charts parity."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module, metadata


@dataclass(frozen=True, slots=True)
class ProviderManifest:
    feature_id: str
    package: str
    version: str
    assets: tuple[str, ...]
    capabilities: tuple[str, ...]


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


def provider_available(feature_id: str) -> bool:
    mapping = {
        "hedron.data": "hedron_data",
        "hedron.charts": "hedron_charts",
    }
    module = mapping.get(feature_id)
    if module is None:
        return False
    try:
        import_module(module)
    except ImportError:
        return False
    return True
