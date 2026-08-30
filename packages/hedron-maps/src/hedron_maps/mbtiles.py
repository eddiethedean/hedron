"""Declared MBTiles archive as a FeatureProvider. sqlite is confined here."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from hedron_core.bundles import FeatureBundle, FeatureRequirement
from hedron_core.catalog import PackageProjection, ProjectionCapability
from hedron_core.codes import HED_MAP_OFFLINE_0001, HED_MAP_OFFLINE_0002
from hedron_core.diagnostics import error
from hedron_maps.limits import MAX_ARCHIVE_BYTES, MAX_ZOOM, MIN_ZOOM
from hedron_maps.spec import MBTiles

__all__ = ["MBTilesArchive", "read_tile"]


def _xyz_to_tms(z: int, y: int) -> int:
    return (2**z - 1) - y


def read_tile(path: Path, *, z: int, x: int, y: int) -> bytes | None:
    if type(z) is not int or type(x) is not int or type(y) is not int:
        raise error(
            HED_MAP_OFFLINE_0002,
            title="MBTiles XYZ must be integers",
            explanation="Non-integer tile indexes are refused.",
            remediation="Use integer z/x/y only.",
        )
    if z < MIN_ZOOM or z > MAX_ZOOM or x < 0 or y < 0 or x >= 2**z or y >= 2**z:
        return None
    resolved = path.resolve()
    if not resolved.is_file():
        raise error(
            HED_MAP_OFFLINE_0001,
            title="MBTiles archive missing",
            explanation=f"{resolved} is not a file.",
            remediation="Declare the archive at construction, not from a request path.",
        )
    query = "SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?"
    with sqlite3.connect(str(resolved)) as con:
        con.execute("PRAGMA query_only=ON")
        row = con.execute(query, (z, x, y)).fetchone()
        if row is None:
            row = con.execute(query, (z, x, _xyz_to_tms(z, y))).fetchone()
    if row is None:
        return None
    data = row[0]
    if isinstance(data, bytes):
        return data
    if isinstance(data, memoryview):
        return bytes(cast(memoryview[Any], data))
    return None


@dataclass(frozen=True, slots=True)
class MBTilesArchive:
    """Construction-time archive handle. Path never comes from a request."""

    archive_id: str
    path: Path
    attribution: str = "Offline map archive"

    def __post_init__(self) -> None:
        if (
            not self.archive_id.replace("-", "").replace("_", "").isalnum()
            or ".." in self.archive_id
        ):
            raise error(
                HED_MAP_OFFLINE_0002,
                title="Invalid MBTiles archive_id",
                explanation="archive_id must be a declared handle, not a filesystem path.",
                remediation="Assign an alphanumeric id when constructing MBTilesArchive.",
            )
        resolved = self.path.expanduser().resolve()
        if not resolved.is_file():
            raise error(
                HED_MAP_OFFLINE_0001,
                title="MBTiles archive missing",
                explanation=f"{resolved} is not a file.",
                remediation="Pass a construction-time path to an existing archive.",
            )
        if resolved.stat().st_size > MAX_ARCHIVE_BYTES:
            raise error(
                HED_MAP_OFFLINE_0001,
                title="MBTiles archive too large",
                explanation=f"Archive exceeds {MAX_ARCHIVE_BYTES} bytes.",
                remediation="Ship a bounded regional extract.",
            )
        object.__setattr__(self, "path", resolved)

    def spec(self) -> MBTiles:
        return MBTiles(archive_id=self.archive_id, attribution=self.attribution)

    def to_bundle(self) -> FeatureBundle:
        archive_id = self.archive_id
        archive_path = self.path
        route = f"/hedron-maps/mbtiles/{archive_id}/{{z}}/{{x}}/{{y}}"

        def tile_route(app: object) -> object:
            getter = getattr(app, "get", None)
            ident = f"hedron-maps-mbtiles-{archive_id}-xyz"
            if not callable(getter):

                def missing() -> None:
                    return None

                tagged: Any = missing
                tagged.logical_id = ident
                return tagged

            def get_tile(z: int, x: int, y: int) -> object:
                from starlette.responses import Response

                blob = read_tile(archive_path, z=z, x=x, y=y)
                if blob is None:
                    return Response(status_code=404)
                return Response(content=blob, media_type="image/png")

            decorator = cast(Callable[..., Any], getter)(
                route, name=f"hedron-maps-mbtiles-{archive_id}"
            )
            registered = decorator(get_tile)
            target: Any = registered if registered is not None else get_tile
            target.logical_id = ident
            return target

        projection = PackageProjection(
            namespace=f"hedron.maps.offline.{archive_id.replace('_', '-')}",
            provider="hedron-maps",
            provider_version="0.1.0",
            capabilities=(ProjectionCapability(name="MBTiles", support="supported"),),
            data={
                "archive_id": archive_id,
                "route": route,
                "integer_xyz": True,
                "request_path": False,
            },
            limitations=(
                "Path is construction-time only",
                "Flagship/adapters own routes via include_feature",
                "Not a general tile server",
            ),
        )
        return FeatureBundle(
            logical_id=f"hedron-maps-mbtiles-{archive_id}",
            provider="hedron-maps",
            provider_version="0.1.0",
            views=(),
            commands=(tile_route,),
            projections=(projection,),
            requirements=(FeatureRequirement(name="hedron-maps", required=True),),
            limitations=("integer XYZ only; sqlite stays in this module",),
        )
