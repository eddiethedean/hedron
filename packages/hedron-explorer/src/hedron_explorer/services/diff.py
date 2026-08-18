"""Deterministic catalog/manifest/route/schema fingerprint diffs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from hedron_core.catalog import compile_interaction_catalog, get_sealed_catalog
from hedron_core.registry import get_registry


def _catalog_fingerprint() -> str:
    live = get_sealed_catalog()
    catalog = live if live is not None else compile_interaction_catalog()
    return str(catalog.fingerprint)


def _route_fingerprint() -> tuple[str, ...]:
    return tuple(sorted(f"{r.kind}:{r.name}:{r.path}" for r in get_registry().routes()))


def _schema_fingerprint() -> tuple[str, ...]:
    catalog = get_sealed_catalog() or compile_interaction_catalog()
    return tuple(
        sorted(
            f"{entry.logical_id}:{entry.type_schema_fingerprint or 'absent'}"
            for entry in catalog.entries.values()
        )
    )


def current_baseline() -> dict[str, Any]:
    catalog = get_sealed_catalog() or compile_interaction_catalog()
    manifest = catalog.to_manifest(profile="development")
    registry = get_registry()
    assets = tuple(sorted(f"{a.logical_id}:{a.kind}" for a in registry.assets()))
    dependencies = tuple(
        sorted(f"{c.logical_id}:{dep}" for c in registry.components() for dep in c.browser_modules)
    )
    from hedron_core.plugins.explorer import get_feature_manifests

    capability_maturity = tuple(
        sorted(f"{f.plugin}:{f.name}:{f.stability}" for f in get_feature_manifests())
    )
    return {
        "catalog": _catalog_fingerprint(),
        "manifest": getattr(manifest, "fingerprint", catalog.fingerprint),
        "routes": list(_route_fingerprint()),
        "schema": list(_schema_fingerprint()),
        "assets": list(assets),
        "dependencies": list(dependencies),
        "capability_maturity": list(capability_maturity),
    }


def diff_baselines(
    before: Mapping[str, Any], after: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    current = after or current_baseline()
    changes: dict[str, Any] = {}
    keys = (
        "catalog",
        "manifest",
        "routes",
        "schema",
        "assets",
        "dependencies",
        "capability_maturity",
    )
    for key in keys:
        old = before.get(key)
        new = current.get(key)
        if old == new:
            changes[key] = {"added": [], "removed": [], "changed": False}
            continue
        if isinstance(old, list) and isinstance(new, list):
            old_set = set(old)
            new_set = set(new)
            changes[key] = {
                "added": sorted(new_set - old_set),
                "removed": sorted(old_set - new_set),
                "changed": True,
            }
        else:
            changes[key] = {
                "added": [],
                "removed": [],
                "changed": old != new,
                "before": old,
                "after": new,
            }
    return {"authority": "explorer-diff-050", "changes": changes}
