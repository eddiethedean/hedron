"""Policy-bounded Map / GeoJSON presentation (RFC-0033).

This is the first-party, CSP-aware Map contract: allowlisted tile templates, feature
budgets, sanitized GeoJSON properties, and a required table/list alternative. It does
**not** load arbitrary remote scripts by default.

MapLibre / Folium / PyDeck remain optional visualization adapters in ``hedron-charts``
and are intentionally separate from this presentation contract.
"""

from __future__ import annotations

import json
import math
from collections.abc import Mapping, Sequence
from typing import TypeGuard, cast

from pydantic import field_validator

from hedron_core.builtins._base import ElementProps, class_names, mark_data
from hedron_core.component import Component, NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.models import Model
from hedron_core.security import SafeUrl, UrlPurpose
from hedron_core.typing_aliases import (
    HtmlAttrMap,
    HtmlAttrValue,
    JsonObject,
    JsonValue,
    is_string_mapping,
)

DEFAULT_MAX_FEATURES = 500

# Property keys that must never drive HTML/JS execution from untrusted GeoJSON.
_DANGEROUS_PROP_KEYS = frozenset(
    {
        "html",
        "__html__",
        "innerhtml",
        "outerhtml",
        "script",
        "javascript",
        "onclick",
        "ondblclick",
        "onmouseover",
        "onload",
        "onerror",
    }
)


def _is_object_sequence(value: object) -> TypeGuard[Sequence[object]]:
    return isinstance(value, (list, tuple))


class MarkerSpec(Model):
    """Declared map marker with optional SafeUrl link or HTMX action path."""

    id: str
    lat: float
    lon: float
    label: str = ""
    href: SafeUrl | None = None
    action: str | None = None

    @field_validator("href", mode="before")
    @classmethod
    def _coerce_href(cls, value: object) -> SafeUrl | None:
        if value is None or value == "":
            return None
        if isinstance(value, SafeUrl):
            return value
        if isinstance(value, str):
            return SafeUrl.parse(value, purpose=UrlPurpose.NAVIGATION)
        raise TypeError(f"href must be SafeUrl or str, got {type(value).__name__}")


class MapProps(ElementProps):
    center_lat: float
    center_lon: float
    zoom: float = 2.0
    width: int | None = None
    height: int | None = 360
    attribution: str = ""
    max_features: int = DEFAULT_MAX_FEATURES
    tiles: str | None = None


class GeoJSONLayer:
    """Validated, sanitized GeoJSON FeatureCollection for ``Map``.

    Nested conceptually under a map; construction fails closed on oversized
    collections and non-finite coordinates. Dangerous property keys are stripped.
    """

    __slots__ = ("geojson", "features")

    def __init__(
        self,
        geojson: Mapping[str, object] | None,
        *,
        max_features: int = DEFAULT_MAX_FEATURES,
    ) -> None:
        self.geojson, self.features = sanitize_geojson(geojson, max_features=max_features)


def _is_dangerous_key(key: str) -> bool:
    lowered = key.lower().strip()
    if lowered in _DANGEROUS_PROP_KEYS:
        return True
    return bool(lowered.startswith("on") and len(lowered) > 2)


def _looks_like_script(value: object) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return (
        "<script" in lowered
        or "javascript:" in lowered
        or "function(" in lowered
        or "</script" in lowered
    )


def _require_finite(value: object, *, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise error(
            "HED-MAP-0003",
            title="Invalid map coordinate",
            explanation=f"{what} must be a finite number, got {type(value).__name__}.",
            remediation="Provide finite float latitude/longitude values.",
        )
    number = float(value)
    if not math.isfinite(number):
        raise error(
            "HED-MAP-0003",
            title="Invalid map coordinate",
            explanation=f"{what} must be finite (rejected NaN/Inf).",
            remediation="Provide finite float latitude/longitude values.",
        )
    return number


def _sanitize_property_value(value: object) -> tuple[bool, JsonValue]:
    if _looks_like_script(value):
        return False, None
    if isinstance(value, Mapping):
        return True, _sanitize_properties(cast(Mapping[object, object], value))
    if _is_object_sequence(value):
        cleaned: list[JsonValue] = []
        for item in value:
            keep, sanitized = _sanitize_property_value(item)
            if keep:
                cleaned.append(sanitized)
        return True, cleaned
    if isinstance(value, float) and not math.isfinite(value):
        return False, None
    if isinstance(value, (str, int, float, bool)) or value is None:
        return True, value
    return True, str(value)


def _sanitize_properties(props: object) -> dict[str, JsonValue]:
    if not isinstance(props, Mapping):
        return {}
    mapping = cast(Mapping[object, object], props)
    cleaned: dict[str, JsonValue] = {}
    for key, value in mapping.items():
        key_s = str(key)
        if _is_dangerous_key(key_s):
            continue
        keep, sanitized = _sanitize_property_value(value)
        if keep:
            cleaned[key_s] = sanitized
    return cleaned


def _validate_coordinates(coords: object, *, depth: int = 0) -> JsonValue:
    if depth > 8:
        raise error(
            "HED-MAP-0003",
            title="Invalid map coordinate",
            explanation="GeoJSON coordinate nesting exceeds the supported depth.",
            remediation="Simplify geometries or reduce nesting.",
        )
    if _is_object_sequence(coords):
        if coords and isinstance(coords[0], (int, float)) and not isinstance(coords[0], bool):
            if len(coords) < 2:
                raise error(
                    "HED-MAP-0003",
                    title="Invalid map coordinate",
                    explanation="Coordinate positions require at least [lon, lat].",
                    remediation="Use GeoJSON position arrays of finite numbers.",
                )
            return [
                _require_finite(coords[0], what="longitude"),
                _require_finite(coords[1], what="latitude"),
                *[_require_finite(v, what="coordinate") for v in coords[2:]],
            ]
        return [_validate_coordinates(item, depth=depth + 1) for item in coords]
    raise error(
        "HED-MAP-0003",
        title="Invalid map coordinate",
        explanation=f"Unexpected coordinate node type {type(coords).__name__}.",
        remediation="Use GeoJSON arrays of finite numbers.",
    )


def _sanitize_geometry(geometry: object) -> JsonObject | None:
    if geometry is None:
        return None
    if not is_string_mapping(geometry):
        raise error(
            "HED-MAP-0003",
            title="Invalid map coordinate",
            explanation="GeoJSON geometry must be an object or null.",
            remediation="Pass a GeoJSON Geometry object.",
        )
    gtype = geometry.get("type")
    if gtype == "GeometryCollection":
        geoms = geometry.get("geometries")
        if geoms is None:
            geoms = ()
        if not _is_object_sequence(geoms):
            raise error(
                "HED-MAP-0003",
                title="Invalid map coordinate",
                explanation="GeometryCollection.geometries must be an array.",
                remediation="Pass a valid GeoJSON GeometryCollection.",
            )
        return {
            "type": "GeometryCollection",
            "geometries": [g for g in (_sanitize_geometry(item) for item in geoms) if g],
        }
    coords = geometry.get("coordinates")
    out: JsonObject = {"type": str(gtype or "Point")}
    if coords is not None:
        out["coordinates"] = _validate_coordinates(coords)
    return out


def _sanitize_feature_id(value: object) -> str | int | float:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        if isinstance(value, bool):
            raise error(
                "HED-MAP-0003",
                title="Invalid GeoJSON feature id",
                explanation="GeoJSON feature ids must be strings or finite numbers, not bool.",
                remediation="Provide a string or finite numeric feature id.",
            )
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        raise error(
            "HED-MAP-0003",
            title="Invalid GeoJSON feature id",
            explanation="GeoJSON feature ids must be finite (rejected NaN/Inf).",
            remediation="Provide a string or finite numeric feature id.",
        )
    return value


def sanitize_geojson(
    geojson: Mapping[str, object] | None,
    *,
    max_features: int = DEFAULT_MAX_FEATURES,
) -> tuple[JsonObject | None, list[JsonObject]]:
    """Validate feature budget/coordinates and strip dangerous properties."""
    if geojson is None:
        return None, []
    raw_geojson: object = geojson
    if not is_string_mapping(raw_geojson):
        raise error(
            "HED-MAP-0001",
            title="Invalid GeoJSON",
            explanation="geojson must be a FeatureCollection mapping or None.",
            remediation="Pass a GeoJSON FeatureCollection dict.",
        )
    features_raw = raw_geojson.get("features")
    if features_raw is None:
        features_raw = ()
    if not _is_object_sequence(features_raw):
        raise error(
            "HED-MAP-0001",
            title="Invalid GeoJSON",
            explanation="FeatureCollection.features must be an array.",
            remediation="Pass a GeoJSON FeatureCollection with a features array.",
        )
    if len(features_raw) > max_features:
        raise error(
            "HED-MAP-0001",
            title="GeoJSON feature budget exceeded",
            explanation=(f"Received {len(features_raw)} features; max_features is {max_features}."),
            remediation="Reduce features server-side or raise max_features explicitly.",
        )
    features: list[JsonObject] = []
    for index, feature in enumerate(features_raw):
        if not is_string_mapping(feature):
            continue
        props = _sanitize_properties(feature.get("properties"))
        geometry = _sanitize_geometry(feature.get("geometry"))
        fid = feature.get("id", index)
        features.append(
            {
                "type": "Feature",
                "id": _sanitize_feature_id(fid),
                "properties": props,
                "geometry": geometry,
            }
        )
    collection = cast(
        JsonObject,
        {
            "type": "FeatureCollection",
            "features": features,
        },
    )
    return collection, features


def _tile_prefix_matches(tiles: str, prefix: str) -> bool:
    """True when ``tiles`` is under ``prefix`` without host-prefix bypass.

    After a successful ``startswith`` match, the next character must be end-of-string
    or a URL boundary (``/``, ``?``, ``#``), unless the prefix already ends on a
    boundary. This rejects ``https://tiles.example`` matching
    ``https://tiles.example.evil.com/...``.
    """
    if not tiles.startswith(prefix):
        return False
    if prefix.endswith(("/", "?", "#")):
        return True
    rest = tiles[len(prefix) :]
    return rest == "" or rest[0] in "/?#"


def _ensure_tile_allowed(tiles: str | None, allowlist: Sequence[str]) -> str | None:
    if tiles is None:
        return None
    prefixes: list[str] = []
    for raw in allowlist:
        prefix = str(raw).strip()
        if not prefix:
            raise error(
                "HED-MAP-0002",
                title="Disallowed map tile source",
                explanation="tile_allowlist entries must be non-empty URL prefixes.",
                remediation=(
                    "Remove empty prefixes and list concrete allowlisted origins or "
                    "path prefixes (prefer a trailing '/' for path prefixes)."
                ),
            )
        prefixes.append(prefix)
    if not prefixes or not any(_tile_prefix_matches(tiles, prefix) for prefix in prefixes):
        raise error(
            "HED-MAP-0002",
            title="Disallowed map tile source",
            explanation=(
                f"Tile template {tiles!r} is not covered by tile_allowlist prefixes {prefixes!r}."
            ),
            remediation=(
                "Pass an allowlisted tile URL prefix via tile_allowlist, or omit tiles "
                "to render the static table alternative only."
            ),
        )
    return tiles


def _coerce_marker(marker: MarkerSpec | Mapping[str, object]) -> MarkerSpec:
    if isinstance(marker, MarkerSpec):
        lat = _require_finite(marker.lat, what="marker.lat")
        lon = _require_finite(marker.lon, what="marker.lon")
        href = marker.href
        action = marker.action
        if action is not None and (not str(action).startswith("/") or str(action).startswith("//")):
            raise error(
                "HED-MAP-0004",
                title="Invalid marker action",
                explanation="Marker action must be a same-origin path starting with '/'.",
                remediation="Use a relative HTMX path such as '/markers/1'.",
            )
        return MarkerSpec(
            id=marker.id,
            lat=lat,
            lon=lon,
            label=marker.label,
            href=href,
            action=action,
        )
    raw_href = marker.get("href")
    href: SafeUrl | None = None
    if isinstance(raw_href, SafeUrl):
        href = raw_href
    elif isinstance(raw_href, str) and raw_href:
        href = SafeUrl.parse(raw_href, purpose=UrlPurpose.NAVIGATION)
    action_val = marker.get("action")
    action = str(action_val) if action_val is not None else None
    return _coerce_marker(
        MarkerSpec(
            id=str(marker.get("id", "")),
            lat=_require_finite(marker.get("lat"), what="marker.lat"),
            lon=_require_finite(marker.get("lon"), what="marker.lon"),
            label=str(marker.get("label") or ""),
            href=href,
            action=action,
        )
    )


def _feature_label(feature: Mapping[str, object], index: int) -> str:
    props = feature.get("properties")
    if is_string_mapping(props):
        for key in ("name", "title", "label", "id"):
            value = props.get(key)
            if isinstance(value, str) and value.strip():
                return value
    fid = feature.get("id")
    if fid is not None and str(fid).strip():
        return str(fid)
    return f"Feature {index + 1}"


def _feature_lat_lon(feature: Mapping[str, object]) -> tuple[str, str]:
    geometry = feature.get("geometry")
    if not is_string_mapping(geometry):
        return ("", "")
    coords = geometry.get("coordinates")
    gtype = geometry.get("type")
    if gtype == "Point" and _is_object_sequence(coords) and len(coords) >= 2:
        return (str(coords[1]), str(coords[0]))
    return ("", "")


class Map(Component[MapProps]):
    """Policy-bounded geographic presentation with a required accessible alternative.

    Progressive enhancement: always emit a table/list of markers and features. An
    optional ``.hedron-map`` container carries allowlisted tile/center data attributes
    for a pinned local map script when assets exist — remote scripts are never injected
    by this component. MapLibre adapters live in ``hedron-charts``, not here.
    """

    props_type = MapProps
    logical_name = "Map"

    def __init__(
        self,
        *,
        center: tuple[float, float] = (0.0, 0.0),
        zoom: float = 2.0,
        width: int | None = None,
        height: int | None = 360,
        tile_allowlist: Sequence[str] = (),
        tiles: str | None = None,
        attribution: str = "",
        markers: Sequence[MarkerSpec | Mapping[str, object]] = (),
        geojson: Mapping[str, object] | GeoJSONLayer | None = None,
        max_features: int = DEFAULT_MAX_FEATURES,
        id: str | None = None,
        class_: str | None = None,
        mark: str | None = None,
        **kwargs: object,
    ) -> None:
        center_lat = _require_finite(center[0], what="center.lat")
        center_lon = _require_finite(center[1], what="center.lon")
        zoom_f = _require_finite(zoom, what="zoom")
        allowed_tiles = _ensure_tile_allowed(tiles, tile_allowlist)
        if isinstance(geojson, GeoJSONLayer):
            sanitized, features = geojson.geojson, list(geojson.features)
            if sanitized is not None and len(features) > max_features:
                raise error(
                    "HED-MAP-0001",
                    title="GeoJSON feature budget exceeded",
                    explanation=(
                        f"Received {len(features)} features; max_features is {max_features}."
                    ),
                    remediation="Reduce features server-side or raise max_features explicitly.",
                )
        else:
            sanitized, features = sanitize_geojson(geojson, max_features=max_features)
        coerced = tuple(_coerce_marker(m) for m in markers)
        super().__init__(
            MapProps(
                center_lat=center_lat,
                center_lon=center_lon,
                zoom=zoom_f,
                width=width,
                height=height,
                attribution=attribution,
                max_features=max_features,
                tiles=allowed_tiles,
                id=id,
                class_=class_,
                mark=mark,
                **kwargs,
            )
        )
        self._tile_allowlist = tuple(tile_allowlist)
        self._markers = coerced
        self._geojson = sanitized
        self._features = features

    def render(self) -> NodeLike:
        table = self._alternative_table()
        enhance_attrs: dict[str, HtmlAttrValue] = {
            "class_": "hedron-map",
            "role": "img",
            "aria": {"label": "Map"},
            "data": {
                "hedron-map": "true",
                "center-lat": str(self.props.center_lat),
                "center-lon": str(self.props.center_lon),
                "zoom": str(self.props.zoom),
            },
        }
        if self.props.width is not None:
            enhance_attrs["width"] = self.props.width
        if self.props.height is not None:
            enhance_attrs["height"] = self.props.height
        data = enhance_attrs["data"]
        if not isinstance(data, dict):
            raise TypeError("Map enhance attrs data must be a dict")
        if self.props.tiles is not None:
            data["tiles"] = self.props.tiles
        if self.props.attribution:
            data["attribution"] = self.props.attribution
        if self._markers:
            data["markers"] = json.dumps(
                [
                    {
                        "id": m.id,
                        "lat": m.lat,
                        "lon": m.lon,
                        "label": m.label,
                        "href": m.href.value if m.href is not None else None,
                        "action": m.action,
                    }
                    for m in self._markers
                ],
                separators=(",", ":"),
            )
        if self._geojson is not None:
            data["geojson"] = json.dumps(
                self._geojson,
                separators=(",", ":"),
                allow_nan=False,
            )

        enhance = html.div(**enhance_attrs)
        parts: list[NodeLike] = [enhance, table]
        if self.props.attribution:
            parts.append(html.p(self.props.attribution, class_="hedron-map-attribution"))

        attrs: dict[str, object] = {
            "class_": class_names("hedron-map-root", self.props.class_),
            "role": "region",
            "aria": {"label": "Geographic map"},
        }
        if self.props.id is not None:
            attrs["id"] = self.props.id
        mark = mark_data(self.props.mark)
        if mark:
            attrs["data"] = mark
        return html.section(*parts, **cast(HtmlAttrMap, attrs))

    def _alternative_table(self) -> NodeLike:
        header = html.tr(
            html.th("Label"),
            html.th("Latitude"),
            html.th("Longitude"),
            html.th("Link"),
        )
        rows: list[NodeLike] = [header]
        for marker in self._markers:
            link_cell: NodeLike
            row_attrs: dict[str, HtmlAttrValue] = {
                "data": {"marker-id": marker.id},
            }
            if marker.href is not None:
                link_cell = html.a(marker.label or marker.id or "Open", href=marker.href)
            elif marker.action:
                link_cell = html.span(marker.action)
                row_attrs["hx-get"] = marker.action
                row_attrs["hx-swap"] = "none"
            else:
                link_cell = html.span("")
            rows.append(
                html.tr(
                    html.td(marker.label or marker.id),
                    html.td(str(marker.lat)),
                    html.td(str(marker.lon)),
                    html.td(link_cell),
                    **row_attrs,
                )
            )
        for index, feature in enumerate(self._features):
            lat, lon = _feature_lat_lon(feature)
            rows.append(
                html.tr(
                    html.td(_feature_label(feature, index)),
                    html.td(lat),
                    html.td(lon),
                    html.td(""),
                    data={"feature-index": str(index)},
                )
            )
        return html.div(
            html.table(
                html.caption("Map features and markers"),
                html.thead(rows[0]),
                html.tbody(*rows[1:]) if len(rows) > 1 else html.tbody(),
                class_="hedron-map-alternative",
            ),
            class_="hedron-map-fallback",
        )


__all__ = [
    "DEFAULT_MAX_FEATURES",
    "GeoJSONLayer",
    "Map",
    "MapProps",
    "MarkerSpec",
    "sanitize_geojson",
]
