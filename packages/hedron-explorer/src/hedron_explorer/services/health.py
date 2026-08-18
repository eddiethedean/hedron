"""Read-only package-health slice. Not hedron package doctor (0.53)."""

from __future__ import annotations

from importlib.metadata import distributions
from typing import Any

from hedron_core.plugins import get_explorer_panels


def package_health() -> dict[str, Any]:
    entries: list[dict[str, str]] = []
    versions: dict[str, str] = {}
    for dist in distributions():
        name = dist.name
        if not str(name).lower().startswith("hedron"):
            continue
        versions[str(name)] = dist.version
        entries.append({"name": str(name), "version": dist.version})
    panels = get_explorer_panels()
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for panel in panels:
        if panel.panel_id in seen:
            duplicates.append(panel.panel_id)
        seen[panel.panel_id] = panel.plugin
    train_versions = {
        k: v
        for k, v in versions.items()
        if k.lower()
        in {
            "hedron",
            "hedron-core",
            "hedron-explorer",
            "hedron-data",
            "hedron-flask",
            "hedron-django",
            "hedron-jinja",
            "hedron-conformance",
            "hedron-extras",
            "hedron-workbench",
            "hedron-posit",
            "hedron-elements",
        }
    }
    skew = len(set(train_versions.values())) > 1
    return {
        "read_only": True,
        "package_doctor": False,
        "entry_points": entries,
        "version_skew": skew,
        "versions": versions,
        "missing_optional_dependencies": [],
        "asset_integrity_csp": {"read_only": True},
        "duplicate_registrations": duplicates,
        "panels": [
            {"panel_id": p.panel_id, "plugin": p.plugin, "title": p.title, "path": p.path}
            for p in panels
        ],
        "conformance_envelope": None,
    }
