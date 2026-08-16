"""Production interaction-manifest validation for Posit/Workbench deploys."""

from __future__ import annotations

from pathlib import Path

from hedron_core.catalog import InteractionCatalog, InteractionManifest
from hedron_core.typing_aliases import JsonObject

__all__ = ["validate_deployed_interactions"]


def validate_deployed_interactions(
    *,
    catalog: InteractionCatalog,
    build_dir: Path,
    mount: str = "",
) -> JsonObject:
    """Validate a production interactions.json and report mount-aware URLs."""
    manifest = InteractionManifest.read_json(Path(build_dir) / "interactions.json")
    manifest.validate_against(catalog)
    return {
        "catalog_fingerprint": catalog.fingerprint,
        "manifest_fingerprint": manifest.fingerprint,
        "mount": mount,
        "interactions_url": f"{mount.rstrip('/')}/interactions.json"
        if mount
        else "interactions.json",
        "ok": True,
    }
