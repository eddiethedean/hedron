"""Offline bundle values. Portable models; sqlite lives in mbtiles.py."""

from __future__ import annotations

from pathlib import Path

from hedron_maps.spec import MBTiles, OfflineMapBundle, PMTiles, StaticImage

SYNTHETIC_ARCHIVE = Path(__file__).resolve().parent / "data" / "synthetic.mbtiles"

__all__ = ["SYNTHETIC_ARCHIVE", "bundle_from_paths", "offline_resource_closed"]


def bundle_from_paths(
    *,
    archive_or_image: str,
    attribution: str,
    hashes: dict[str, str],
    style: str | None = None,
    sprites: str | None = None,
    glyphs: str | None = None,
) -> OfflineMapBundle:
    return OfflineMapBundle(
        archive_or_image=archive_or_image,
        attribution=attribution,
        hashes=hashes,
        style=style,
        sprites=sprites,
        glyphs=glyphs,
    )


def offline_resource_closed(values: object) -> bool:
    """True when every declared resource is a same-origin path or hash-named local id."""
    if isinstance(values, OfflineMapBundle):
        items = (
            values.archive_or_image,
            values.style,
            values.sprites,
            values.glyphs,
        )
    elif isinstance(values, (StaticImage, PMTiles)):
        items = (getattr(values, "src", None), getattr(values, "style", None))
    elif isinstance(values, MBTiles):
        items = (values.route_template,)
    else:
        return False
    for item in items:
        if not item:
            continue
        if item.startswith("https://") or item.startswith("http://") or item.startswith("//"):
            return False
        if ".." in item:
            return False
    return True
