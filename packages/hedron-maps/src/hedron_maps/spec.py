"""Closed MapSpec / MapPlan grammar (SPEC-047 / MAP-SPEC-001)."""

from __future__ import annotations

from typing import Annotated, Literal, cast

from pydantic import BaseModel, ConfigDict, Field

from hedron_core.typing_aliases import JsonObject

SCHEMA_VERSION = 1
SCHEMA_ID = "hedron-map-spec/1"

OSM_STANDARD_ID = "openstreetmap-standard"
OSM_STANDARD_ATTRIBUTION = "© OpenStreetMap contributors"
OSM_STANDARD_TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
OSM_STANDARD_ORIGIN = "https://tile.openstreetmap.org"

SourceKind = Literal[
    "openstreetmap-standard",
    "xyz-raster",
    "tilejson",
    "mvt-vector",
    "static-image",
    "pmtiles",
    "mbtiles",
    "none",
]
LayerKind = Literal["marker", "geojson", "line", "polygon", "circle", "raster"]
Scheme = Literal["xyz", "tms"]
ThemeMode = Literal["light", "dark", "forced-colors"]
FitPolicy = Literal["none", "layers"]


class MapModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Bounds(MapModel):
    west: float
    south: float
    east: float
    north: float


class ViewState(MapModel):
    center: tuple[float, float] = (0.0, 0.0)
    zoom: float = 2.0
    bearing: float = 0.0
    pitch: float = 0.0
    fit: FitPolicy = "none"
    padding: float = 0.0


class MapTheme(MapModel):
    mode: ThemeMode = "light"
    tokens: dict[str, str] = Field(default_factory=dict)


class MapStyle(MapModel):
    """Locked safe MapLibre style subset. Not a public MapLibre options dict."""

    version: int = 8
    name: str | None = None
    # object (not hedron JsonValue): pydantic cannot resolve that recursive TypeAlias.
    sources: dict[str, dict[str, object]] = Field(default_factory=dict)
    layers: tuple[dict[str, object], ...] = ()
    glyphs: str | None = None
    sprite: str | None = None


class MapPolicy(MapModel):
    allowed_origins: tuple[str, ...] = ()
    allowed_source_kinds: tuple[SourceKind, ...] = (
        "openstreetmap-standard",
        "xyz-raster",
        "tilejson",
        "mvt-vector",
        "static-image",
        "pmtiles",
        "mbtiles",
        "none",
    )
    remote_requests_permitted: bool = True
    allow_proxy: bool = False


class OpenStreetMap(MapModel):
    kind: Literal["openstreetmap-standard"] = "openstreetmap-standard"
    tile_url: str = OSM_STANDARD_TILE_URL
    attribution: str = OSM_STANDARD_ATTRIBUTION
    min_zoom: int = 0
    max_zoom: int = 19
    tile_size: int = 256
    scale: str | None = None
    subdomain: str | None = None

    @classmethod
    def standard(cls) -> OpenStreetMap:
        return cls()


class RasterTiles(MapModel):
    kind: Literal["xyz-raster"] = "xyz-raster"
    url: str
    attribution: str
    tile_size: int = 256
    min_zoom: int = 0
    max_zoom: int = 18
    scheme: Scheme = "xyz"
    scale: str | None = None
    subdomain: str | None = None


class TileJSON(MapModel):
    kind: Literal["tilejson"] = "tilejson"
    attribution: str
    url: str | None = None
    # object (not hedron JsonValue): pydantic cannot resolve that recursive TypeAlias.
    document: dict[str, object] | None = None


class VectorTiles(MapModel):
    kind: Literal["mvt-vector"] = "mvt-vector"
    url: str
    attribution: str
    min_zoom: int = 0
    max_zoom: int = 14
    style: MapStyle | None = None


class StaticImage(MapModel):
    kind: Literal["static-image"] = "static-image"
    src: str
    attribution: str = ""
    bounds: tuple[float, float, float, float] | None = None


class PMTiles(MapModel):
    kind: Literal["pmtiles"] = "pmtiles"
    src: str
    attribution: str = ""
    style: str | None = None
    vector: bool = False


class MBTiles(MapModel):
    """Declared archive handle. Construction-time id only; never a request path."""

    kind: Literal["mbtiles"] = "mbtiles"
    archive_id: str
    attribution: str = ""
    min_zoom: int = 0
    max_zoom: int = 14
    route_template: str = "/hedron-maps/mbtiles/{archive_id}/{z}/{x}/{y}"


class NoBasemap(MapModel):
    kind: Literal["none"] = "none"


class OfflineMapBundle(MapModel):
    archive_or_image: str
    attribution: str
    hashes: dict[str, str]
    style: str | None = None
    sprites: str | None = None
    glyphs: str | None = None
    bounds: Bounds | None = None
    packaging_metadata: dict[str, str] = Field(default_factory=dict)


class MarkerLayer(MapModel):
    kind: Literal["marker"] = "marker"
    # object (not hedron JsonValue): pydantic cannot resolve that recursive TypeAlias.
    markers: tuple[dict[str, object], ...] = ()


class GeoJSONLayer(MapModel):
    """Typed overlay layer (hedron_maps.GeoJSONLayer).

    Distinct from the core sanitizer wrapper ``hedron_core.GeoJSONLayer``.
    """

    kind: Literal["geojson"] = "geojson"
    # object (not hedron JsonValue): pydantic cannot resolve that recursive TypeAlias.
    data: dict[str, object]
    paint: dict[str, object] | None = None


class LineLayer(MapModel):
    kind: Literal["line"] = "line"
    data: dict[str, object]
    paint: dict[str, object] | None = None


class PolygonLayer(MapModel):
    kind: Literal["polygon"] = "polygon"
    data: dict[str, object]
    paint: dict[str, object] | None = None


class CircleLayer(MapModel):
    kind: Literal["circle"] = "circle"
    data: dict[str, object]
    paint: dict[str, object] | None = None


class RasterLayer(MapModel):
    kind: Literal["raster"] = "raster"
    source: str
    paint: dict[str, object] | None = None


class AccessibilityDef(MapModel):
    title: str
    description: str
    decorative: bool = False
    include_table: bool = True


class ControlsDef(MapModel):
    navigation: bool = True
    attribution: bool = True
    scale: bool = False
    geolocate: bool = False


Basemap = (
    OpenStreetMap
    | RasterTiles
    | TileJSON
    | VectorTiles
    | StaticImage
    | PMTiles
    | MBTiles
    | NoBasemap
)
Layer = MarkerLayer | GeoJSONLayer | LineLayer | PolygonLayer | CircleLayer | RasterLayer
BasemapField = Annotated[Basemap, Field(discriminator="kind")]
LayerField = Annotated[Layer, Field(discriminator="kind")]


class MapSpec(MapModel):
    """Immutable, JSON-serializable, schema-versioned map specification."""

    schema_version: int = SCHEMA_VERSION
    basemap: BasemapField | None = None
    layers: tuple[LayerField, ...] = ()
    view: ViewState = Field(default_factory=ViewState)
    controls: ControlsDef = Field(default_factory=ControlsDef)
    theme: MapTheme = Field(default_factory=MapTheme)
    accessibility: AccessibilityDef
    policy: MapPolicy | None = None
    interactions: tuple[str, ...] = ()

    def to_json_dict(self) -> JsonObject:
        return cast(JsonObject, self.model_dump(mode="json"))


class AccessibilityPlan(MapModel):
    title: str
    description: str
    include_table: bool = True
    table_rows: tuple[dict[str, object], ...] = ()
    decorative: bool = False


class MapPlan(MapModel):
    """Deterministic compilation result consumed by host, fallback, Explorer."""

    schema_id: str = SCHEMA_ID
    schema_version: int = SCHEMA_VERSION
    spec_fingerprint: str
    plan_fingerprint: str
    # object (not hedron JsonValue): pydantic cannot resolve that recursive TypeAlias.
    renderer: dict[str, object]
    resources: tuple[str, ...] = ()
    origins: tuple[str, ...] = ()
    csp: dict[str, str] = Field(default_factory=dict)
    attribution: tuple[str, ...] = ()
    fallback: dict[str, object] = Field(default_factory=dict)
    bounds: Bounds | None = None
    view: ViewState = Field(default_factory=ViewState)
    layers: tuple[dict[str, object], ...] = ()
    style: dict[str, object] = Field(default_factory=dict)
    limits: dict[str, int] = Field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    accessibility: AccessibilityPlan
    events: tuple[str, ...] = ()
    failure_states: tuple[str, ...] = (
        "loading",
        "empty",
        "unsupported",
        "renderer",
        "source",
        "partial",
    )
    source_kind: SourceKind = "none"
    preset_id: str | None = None

    def to_json_dict(self) -> JsonObject:
        return cast(JsonObject, self.model_dump(mode="json"))
