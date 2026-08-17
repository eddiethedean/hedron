"""MapSpec → MapPlan compiler (SPEC-047 / PROVIDER-047). No I/O."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from typing import Any
from urllib.parse import urlparse

from hedron_core.builtins.map_geo import DEFAULT_MAX_FEATURES, MarkerSpec, sanitize_geojson
from hedron_core.codes import (
    HED_MAP_0004,
    HED_MAP_POLICY_0001,
    HED_MAP_POLICY_0002,
    HED_MAP_SOURCE_0001,
    HED_MAP_SOURCE_0002,
    HED_MAP_SOURCE_0003,
    HED_MAP_SPEC_0001,
    HED_MAP_SPEC_0002,
    HED_MAP_SPEC_0003,
    HED_MAP_SPEC_0004,
    HED_MAP_STYLE_0001,
    HED_MAP_STYLE_0002,
)
from hedron_core.diagnostics import HedronError, error
from hedron_maps.limits import (
    LIMITS,
    MAX_COORD_COUNT,
    MAX_FEATURES,
    MAX_LAYERS_PER_MAP,
    MAX_PLAN_BYTES,
    MAX_SOURCES_PER_MAP,
    MAX_STYLE_BYTES,
    MAX_TILEJSON_BYTES,
    MAX_ZOOM,
    MIN_ZOOM,
)
from hedron_maps.spec import (
    OSM_STANDARD_ID,
    OSM_STANDARD_ORIGIN,
    SCHEMA_ID,
    SCHEMA_VERSION,
    AccessibilityPlan,
    Bounds,
    Layer,
    MapPlan,
    MapPolicy,
    MapSpec,
    MapStyle,
    MarkerLayer,
    MBTiles,
    NoBasemap,
    OfflineMapBundle,
    OpenStreetMap,
    PMTiles,
    RasterLayer,
    RasterTiles,
    StaticImage,
    TileJSON,
    VectorTiles,
)

REQUIRED_PLACEHOLDERS = ("{z}", "{x}", "{y}")
OPT_IN_PLACEHOLDERS = ("{scale}", "{s}", "{subdomain}")
UNSAFE_SCHEMES = frozenset({"javascript", "data", "blob", "file", "ftp", "ws", "wss"})
FORBIDDEN_STYLE_KEYS = frozenset(
    {
        "filter-eval",
        "expression-eval",
        "promoteId-callback",
        "__proto__",
        "constructor",
        "prototype",
    }
)
ALLOWED_STYLE_LAYER_TYPES = frozenset(
    {"background", "fill", "line", "symbol", "circle", "raster", "fill-extrusion"}
)
MAPLIBRE_PIN = "5.6.1"

__all__ = ["compile_map", "parse_map_spec"]


def _map_error(code: str, title: str, explanation: str, remediation: str) -> HedronError:
    return error(code, title=title, explanation=explanation, remediation=remediation)


def _fingerprint(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _reject_pollution(obj: object, path: str = "$") -> None:
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            key_s = str(key)
            if key_s in {"__proto__", "constructor", "prototype"}:
                raise _map_error(
                    HED_MAP_SPEC_0001,
                    "Prototype-pollution key rejected",
                    f"Forbidden key {key_s!r} at {path}.",
                    "Remove prototype-pollution keys from MapSpec payloads.",
                )
            _reject_pollution(value, f"{path}.{key_s}")
    elif isinstance(obj, (list, tuple)):
        for index, item in enumerate(obj):
            _reject_pollution(item, f"{path}[{index}]")


def _byte_size(payload: object) -> int:
    return len(json.dumps(payload, default=str, separators=(",", ":")).encode("utf-8"))


def parse_map_spec(raw: MapSpec | Mapping[str, Any]) -> MapSpec:
    if isinstance(raw, MapSpec):
        _reject_pollution(raw.to_json_dict())
        return raw
    _reject_pollution(raw)
    try:
        return MapSpec.model_validate(dict(raw))
    except Exception as exc:
        raise _map_error(
            HED_MAP_SPEC_0001,
            "Invalid MapSpec",
            str(exc),
            "Use a schema-versioned MapSpec with known fields only.",
        ) from exc


def _require_title(spec: MapSpec) -> None:
    acc = spec.accessibility
    if acc.decorative:
        return
    if not acc.title.strip() or not acc.description.strip():
        raise _map_error(
            HED_MAP_SPEC_0004,
            "Map accessibility requires title and description",
            "Non-decorative maps need a useful title and description.",
            "Pass accessibility=AccessibilityDef(title=..., description=...) or mark decorative.",
        )


def _origin_of(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None


def _validate_url(url: str, *, allow_relative: bool = True) -> str:
    if url.startswith("//"):
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Protocol-relative URL rejected",
            f"Refused {url!r}.",
            "Use https:// or a same-origin relative path.",
        )
    if "\\" in url:
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Unsafe URL rejected",
            f"Refused {url!r}.",
            "Use a canonical HTTPS or same-origin path.",
        )
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        raise _map_error(
            HED_MAP_POLICY_0002,
            "URL credentials rejected",
            "Plans must not contain userinfo or embedded credentials.",
            "Strip credentials; use application-owned authz, not tile URL secrets.",
        )
    if parsed.scheme and parsed.scheme.lower() in UNSAFE_SCHEMES:
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Unsafe URL scheme rejected",
            f"Scheme {parsed.scheme!r} is not allowed in map resources.",
            "Use https for remote production resources or same-origin relative paths.",
        )
    if parsed.scheme == "http":
        raise _map_error(
            HED_MAP_POLICY_0002,
            "HTTP remote tiles rejected",
            "Remote production tiles must be HTTPS.",
            "Serve tiles over https:// or use a same-origin asset path.",
        )
    if not parsed.scheme:
        if not allow_relative or not url.startswith("/"):
            raise _map_error(
                HED_MAP_SOURCE_0001,
                "Relative resource must be a same-origin path",
                f"Refused {url!r}.",
                "Use a leading-slash same-origin path such as /assets/maps/....",
            )
        return url
    if parsed.scheme != "https":
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Unsupported URL scheme",
            f"Scheme {parsed.scheme!r} is not https.",
            "Use https or a same-origin path.",
        )
    return url


_PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}")


def _validate_template(url: str, *, scale: str | None, subdomain: str | None) -> None:
    _validate_url(url, allow_relative=True)
    for required in REQUIRED_PLACEHOLDERS:
        if required not in url:
            raise _map_error(
                HED_MAP_SOURCE_0001,
                "Tile template missing required placeholder",
                f"Template {url!r} must include {{z}}, {{x}}, and {{y}}.",
                "Use an XYZ template with {z}{x}{y}.",
            )
    found = set(_PLACEHOLDER_RE.findall(url))
    allowed: set[str] = set(REQUIRED_PLACEHOLDERS)
    if scale is not None:
        allowed.add("{scale}")
    if subdomain is not None:
        allowed.update(("{s}", "{subdomain}"))
    extra = found - allowed
    if extra:
        raise _map_error(
            HED_MAP_SOURCE_0001,
            "Unsupported tile template placeholder",
            f"Placeholders {sorted(extra)} are not in the locked opt-in set.",
            "Only {z}{x}{y} are required; scale/subdomain are explicit opt-in fields.",
        )


def _policy_allows(origin: str | None, policy: MapPolicy, *, local: bool) -> None:
    if origin is None:
        if local:
            return
        raise _map_error(
            HED_MAP_POLICY_0001,
            "Remote origin missing",
            "A remote source did not produce an exact HTTPS origin.",
            "Use an https URL with a host.",
        )
    allowed = tuple(policy.allowed_origins)
    if origin not in allowed:
        raise _map_error(
            HED_MAP_POLICY_0001,
            "Origin not in MapPolicy.allowed_origins",
            f"{origin} is not an exact allowed origin.",
            "Add the exact HTTPS origin to MapPolicy(allowed_origins=...).",
        )


def _zoom_ok(min_zoom: int, max_zoom: int) -> None:
    if min_zoom < MIN_ZOOM or max_zoom > MAX_ZOOM or min_zoom > max_zoom:
        raise _map_error(
            HED_MAP_SPEC_0003,
            "Zoom out of bounds",
            f"Zoom range {min_zoom}..{max_zoom} exceeds {MIN_ZOOM}..{MAX_ZOOM}.",
            "Use a zoom range within the Stage 1 measured limits.",
        )


def _count_coords(obj: object, *, depth: int = 0) -> int:
    if depth > 8:
        return 0
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        if obj and all(isinstance(item, (int, float)) for item in obj):
            return 1
        return sum(_count_coords(item, depth=depth + 1) for item in obj)
    return 0


def _layer_geojson(layer: Layer) -> Mapping[str, Any] | None:
    data = getattr(layer, "data", None)
    return data if isinstance(data, Mapping) else None


def _sanitize_layer(layer: Layer, *, max_features: int) -> dict[str, Any]:
    dumped = layer.model_dump(mode="json")
    geo = _layer_geojson(layer)
    if geo is not None:
        cleaned, features = sanitize_geojson(geo, max_features=max_features)
        dumped["data"] = cleaned or {"type": "FeatureCollection", "features": []}
        dumped["feature_count"] = len(features)
        coords = _count_coords((cleaned or {}).get("features") if cleaned else [])
        if coords > MAX_COORD_COUNT:
            raise _map_error(
                HED_MAP_SPEC_0002,
                "GeoJSON coordinate budget exceeded",
                f"Counted {coords} coordinate positions; max is {MAX_COORD_COUNT}.",
                "Simplify geometries server-side before compile_map.",
            )
        encoded = json.dumps(dumped.get("data"), separators=(",", ":")).encode("utf-8")
        if len(encoded) > MAX_PLAN_BYTES:
            raise _map_error(
                HED_MAP_SPEC_0002,
                "Layer payload too large",
                "GeoJSON layer exceeds the plan byte budget.",
                "Reduce properties or feature count.",
            )
    if isinstance(layer, MarkerLayer) and len(layer.markers) > max_features:
        raise _map_error(
            HED_MAP_SPEC_0002,
            "Marker budget exceeded",
            f"{len(layer.markers)} markers exceeds {max_features}.",
            "Reduce markers or raise max_features explicitly at the call site.",
        )
    return dumped


def _style_subset(
    style: MapStyle | Mapping[str, Any] | None, *, origins: list[str], policy: MapPolicy
) -> dict[str, Any]:
    if style is None:
        return {"version": 8, "sources": {}, "layers": []}
    dumped = style.model_dump(mode="json") if isinstance(style, MapStyle) else dict(style)
    _reject_pollution(dumped)
    if _byte_size(dumped) > MAX_STYLE_BYTES:
        raise _map_error(
            HED_MAP_SPEC_0002,
            "Style budget exceeded",
            f"Style JSON exceeds {MAX_STYLE_BYTES} bytes.",
            "Ship a smaller locked style subset.",
        )
    for key in dumped:
        if str(key) in FORBIDDEN_STYLE_KEYS:
            raise _map_error(
                HED_MAP_STYLE_0001,
                "Unsafe style key rejected",
                f"Style key {key!r} is not in the locked subset.",
                "Remove callbacks, eval, and prototype keys from MapStyle.",
            )
    for layer in dumped.get("layers") or ():
        if isinstance(layer, Mapping) and layer.get("type") not in ALLOWED_STYLE_LAYER_TYPES:
            raise _map_error(
                HED_MAP_STYLE_0001,
                "Unsupported style layer type",
                f"Layer type {layer.get('type')!r} is outside the locked subset.",
                "Use fill/line/symbol/circle/raster/background layers.",
            )
    for field in ("glyphs", "sprite"):
        value = dumped.get(field)
        if isinstance(value, str) and value:
            checked = _validate_url(value)
            origin = _origin_of(checked)
            if origin:
                _policy_allows(origin, policy, local=False)
                if origin not in origins:
                    origins.append(origin)
            dumped[field] = checked
    for source in (dumped.get("sources") or {}).values():
        if not isinstance(source, Mapping):
            continue
        tiles = source.get("tiles")
        if isinstance(tiles, Sequence):
            for tile in tiles:
                if isinstance(tile, str):
                    checked = _validate_url(tile)
                    origin = _origin_of(checked)
                    if origin:
                        _policy_allows(origin, policy, local=False)
                        if origin not in origins:
                            origins.append(origin)
        url = source.get("url")
        if isinstance(url, str) and url:
            checked = _validate_url(url)
            origin = _origin_of(checked)
            if origin:
                _policy_allows(origin, policy, local=False)
                if origin not in origins:
                    origins.append(origin)
    if (dumped.get("glyphs") or dumped.get("sprite")) and any(
        key in dumped for key in ("owner", "metadata-url")
    ):
        raise _map_error(
            HED_MAP_STYLE_0002,
            "Style resource graph is not closed",
            "Unexpected remote metadata remained after origin closure.",
            "Declare every sprite/glyph/source origin in policy.",
        )
    return dumped


def _basemap_facts(
    spec: MapSpec,
    policy: MapPolicy,
) -> tuple[str, str | None, list[str], list[str], list[str], dict[str, Any], list[str]]:
    """Return kind, preset id, resources, origins, attribution, style, warnings."""
    basemap = spec.basemap
    warnings: list[str] = []
    origins: list[str] = []
    resources: list[str] = []
    attribution: list[str] = []
    style: dict[str, Any] = {"version": 8, "sources": {}, "layers": []}

    if basemap is None:
        return "none", None, resources, origins, attribution, style, warnings

    kind = getattr(basemap, "kind", None)
    if kind not in policy.allowed_source_kinds:
        raise _map_error(
            HED_MAP_SOURCE_0002,
            "Source kind is not allowed",
            f"Kind {kind!r} is outside MapPolicy.allowed_source_kinds.",
            "Permit the kind explicitly or use a Supported catalog source.",
        )

    attr = str(getattr(basemap, "attribution", "") or "")
    if kind != "none" and not attr.strip():
        raise _map_error(
            HED_MAP_SOURCE_0003,
            "Attribution required",
            f"Source kind {kind} must carry visible attribution.",
            "Pass attribution= on the basemap value.",
        )
    if attr:
        attribution.append(attr)

    if isinstance(basemap, OpenStreetMap):
        _validate_template(basemap.tile_url, scale=basemap.scale, subdomain=basemap.subdomain)
        _zoom_ok(basemap.min_zoom, basemap.max_zoom)
        origin = _origin_of(basemap.tile_url) or OSM_STANDARD_ORIGIN
        if origin != OSM_STANDARD_ORIGIN or (
            policy.allowed_origins and origin not in policy.allowed_origins
        ):
            _policy_allows(origin, policy, local=False)
        origins.append(origin)
        resources.append(basemap.tile_url)
        style["sources"]["basemap"] = {
            "type": "raster",
            "tiles": [basemap.tile_url],
            "tileSize": basemap.tile_size,
            "attribution": attr,
        }
        style["layers"] = [{"id": "basemap", "type": "raster", "source": "basemap"}]
        warnings.append("OSM standard preset is replaceable and has no availability/SLA claim.")
        return str(kind), OSM_STANDARD_ID, resources, origins, attribution, style, warnings

    if isinstance(basemap, RasterTiles):
        _validate_template(basemap.url, scale=basemap.scale, subdomain=basemap.subdomain)
        _zoom_ok(basemap.min_zoom, basemap.max_zoom)
        origin = _origin_of(basemap.url)
        _policy_allows(origin, policy, local=origin is None)
        if origin:
            origins.append(origin)
        resources.append(basemap.url)
        style["sources"]["basemap"] = {
            "type": "raster",
            "tiles": [basemap.url],
            "tileSize": basemap.tile_size,
            "scheme": basemap.scheme,
            "attribution": attr,
        }
        style["layers"] = [{"id": "basemap", "type": "raster", "source": "basemap"}]
        return str(kind), None, resources, origins, attribution, style, warnings

    if isinstance(basemap, TileJSON):
        if basemap.document is not None:
            if _byte_size(basemap.document) > MAX_TILEJSON_BYTES:
                raise _map_error(
                    HED_MAP_SPEC_0002,
                    "TileJSON document too large",
                    f"TileJSON exceeds {MAX_TILEJSON_BYTES} bytes.",
                    "Trim the TileJSON document before compile_map.",
                )
            _reject_pollution(basemap.document)
            tiles = basemap.document.get("tiles") if isinstance(basemap.document, Mapping) else None
            if isinstance(tiles, Sequence):
                for tile in tiles:
                    if isinstance(tile, str):
                        _validate_url(tile)
                        origin = _origin_of(tile)
                        _policy_allows(origin, policy, local=origin is None)
                        if origin and origin not in origins:
                            origins.append(origin)
                        resources.append(tile)
        if basemap.url:
            checked = _validate_url(basemap.url)
            origin = _origin_of(checked)
            _policy_allows(origin, policy, local=origin is None)
            if origin:
                origins.append(origin)
            resources.append(checked)
        return str(kind), None, resources, origins, attribution, style, warnings

    if isinstance(basemap, VectorTiles):
        _validate_template(basemap.url, scale=None, subdomain=None)
        _zoom_ok(basemap.min_zoom, basemap.max_zoom)
        origin = _origin_of(basemap.url)
        _policy_allows(origin, policy, local=origin is None)
        if origin:
            origins.append(origin)
        resources.append(basemap.url)
        style = _style_subset(basemap.style, origins=origins, policy=policy)
        style.setdefault("sources", {})["basemap"] = {
            "type": "vector",
            "tiles": [basemap.url],
            "attribution": attr,
        }
        return str(kind), None, resources, origins, attribution, style, warnings

    if isinstance(basemap, StaticImage):
        checked = _validate_url(basemap.src)
        origin = _origin_of(checked)
        if origin:
            _policy_allows(origin, policy, local=False)
            origins.append(origin)
        resources.append(checked)
        return str(kind), None, resources, origins, attribution, style, warnings

    if isinstance(basemap, PMTiles):
        checked = _validate_url(basemap.src)
        origin = _origin_of(checked)
        if origin:
            _policy_allows(origin, policy, local=False)
            origins.append(origin)
        resources.append(checked)
        if basemap.style:
            style_url = _validate_url(basemap.style)
            style_origin = _origin_of(style_url)
            if style_origin:
                _policy_allows(style_origin, policy, local=False)
                if style_origin not in origins:
                    origins.append(style_origin)
            resources.append(style_url)
        return str(kind), None, resources, origins, attribution, style, warnings

    if isinstance(basemap, MBTiles):
        if not basemap.archive_id.replace("-", "").replace("_", "").isalnum():
            raise _map_error(
                HED_MAP_SOURCE_0001,
                "MBTiles archive_id is not a declared handle",
                "archive_id must be an alphanumeric declared id, not a filesystem path.",
                "Pass archive_id= at construction; never read a path from a request.",
            )
        if "/" in basemap.archive_id or "\\" in basemap.archive_id or ".." in basemap.archive_id:
            raise _map_error(
                HED_MAP_SOURCE_0001,
                "MBTiles archive_id looks like a path",
                f"Refused archive_id {basemap.archive_id!r}.",
                "Use a declared handle; routes stay integer XYZ only.",
            )
        resources.append(basemap.route_template.replace("{archive_id}", basemap.archive_id))
        return str(kind), None, resources, origins, attribution, style, warnings

    if isinstance(basemap, NoBasemap):
        return "none", None, resources, origins, attribution, style, warnings

    if isinstance(basemap, OfflineMapBundle):
        for field in ("archive_or_image", "style", "sprites", "glyphs"):
            value = getattr(basemap, field, None)
            if isinstance(value, str) and value:
                checked = _validate_url(value)
                origin = _origin_of(checked)
                if origin:
                    _policy_allows(origin, policy, local=False)
                    if origin not in origins:
                        origins.append(origin)
                resources.append(checked)
        if basemap.attribution:
            attribution.append(basemap.attribution)
        return "pmtiles", None, resources, origins, attribution, style, warnings

    raise _map_error(
        HED_MAP_SOURCE_0002,
        "Unknown basemap type",
        f"Unsupported basemap {type(basemap).__name__}.",
        "Use a Supported catalog source kind.",
    )


def _fallback_rows(spec: MapSpec, layers: Sequence[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    rows: list[dict[str, Any]] = []
    for layer in spec.layers:
        if isinstance(layer, MarkerLayer):
            for marker in layer.markers:
                rows.append(
                    {
                        "id": str(marker.get("id", "")),
                        "label": str(marker.get("label") or marker.get("id") or ""),
                        "lat": marker.get("lat"),
                        "lon": marker.get("lon"),
                        "href": marker.get("href"),
                        "action": marker.get("action"),
                    }
                )
        geo = _layer_geojson(layer)
        if geo is None:
            continue
        _, features = sanitize_geojson(geo, max_features=MAX_FEATURES)
        for index, feature in enumerate(features):
            props = feature.get("properties") if isinstance(feature, Mapping) else {}
            label = ""
            if isinstance(props, Mapping):
                for key in ("name", "title", "label", "id"):
                    value = props.get(key)
                    if isinstance(value, str) and value.strip():
                        label = value
                        break
            geometry = feature.get("geometry") if isinstance(feature, Mapping) else None
            lat = lon = None
            if isinstance(geometry, Mapping) and geometry.get("type") == "Point":
                coords = geometry.get("coordinates")
                if isinstance(coords, Sequence) and len(coords) >= 2:
                    lon, lat = coords[0], coords[1]
            rows.append(
                {"id": str(feature.get("id", index)), "label": label, "lat": lat, "lon": lon}
            )
    return tuple(rows[:MAX_FEATURES])


def compile_map(
    spec: MapSpec | Mapping[str, Any],
    policy: MapPolicy | None = None,
    *,
    max_features: int = DEFAULT_MAX_FEATURES,
) -> MapPlan:
    """Compile an already materialized spec. Performs no I/O."""
    parsed = parse_map_spec(spec)
    if parsed.schema_version != SCHEMA_VERSION:
        raise _map_error(
            HED_MAP_SPEC_0001,
            "Unsupported MapSpec schema_version",
            f"Got {parsed.schema_version}; expected {SCHEMA_VERSION}.",
            "Rebuild the spec with schema_version=1.",
        )
    _require_title(parsed)
    if len(parsed.layers) > MAX_LAYERS_PER_MAP:
        raise _map_error(
            HED_MAP_SPEC_0002,
            "Layer budget exceeded",
            f"{len(parsed.layers)} layers exceeds {MAX_LAYERS_PER_MAP}.",
            "Split maps or reduce overlay layers.",
        )
    if not (MIN_ZOOM <= parsed.view.zoom <= MAX_ZOOM):
        raise _map_error(
            HED_MAP_SPEC_0003,
            "View zoom out of bounds",
            f"zoom={parsed.view.zoom} is outside {MIN_ZOOM}..{MAX_ZOOM}.",
            "Choose a zoom within the Stage 1 measured range.",
        )

    effective = policy or parsed.policy or MapPolicy()
    if parsed.basemap is None:
        resolved_policy = effective
        kind, preset, resources, origins, attribution, style, warnings = _basemap_facts(
            parsed, resolved_policy
        )
    elif isinstance(parsed.basemap, OpenStreetMap) and not effective.allowed_origins:
        origin = _origin_of(parsed.basemap.tile_url)
        if origin in {None, OSM_STANDARD_ORIGIN}:
            resolved_policy = MapPolicy(
                allowed_origins=(OSM_STANDARD_ORIGIN,),
                allowed_source_kinds=effective.allowed_source_kinds,
                remote_requests_permitted=effective.remote_requests_permitted,
                allow_proxy=effective.allow_proxy,
            )
        else:
            resolved_policy = effective
        kind, preset, resources, origins, attribution, style, warnings = _basemap_facts(
            parsed, resolved_policy
        )
    else:
        resolved_policy = effective
        kind, preset, resources, origins, attribution, style, warnings = _basemap_facts(
            parsed, resolved_policy
        )

    source_count = 1 if kind != "none" else 0
    for layer in parsed.layers:
        if isinstance(layer, RasterLayer):
            source_count += 1
    if source_count > MAX_SOURCES_PER_MAP:
        raise _map_error(
            HED_MAP_SPEC_0002,
            "Source budget exceeded",
            f"{source_count} sources exceeds {MAX_SOURCES_PER_MAP}.",
            "Combine overlays or split maps.",
        )

    compiled_layers = tuple(
        _sanitize_layer(layer, max_features=max_features) for layer in parsed.layers
    )
    rows = _fallback_rows(parsed, compiled_layers)
    for marker in compiled_layers:
        if marker.get("kind") == "marker":
            for item in marker.get("markers") or ():
                if item.get("action") and item.get("href"):
                    raise _map_error(
                        HED_MAP_0004,
                        "Marker cannot mix href and action",
                        "Reuse HED-MAP-0004 semantics: one ordinary action path per marker.",
                        "Supply href or action, not both.",
                    )
                MarkerSpec.model_validate(
                    {
                        "id": str(item.get("id") or "marker"),
                        "lat": item.get("lat") or 0.0,
                        "lon": item.get("lon") or 0.0,
                        "label": str(item.get("label") or ""),
                    }
                )

    renderer = {
        "engine": "maplibre",
        "version": MAPLIBRE_PIN,
        "strict_csp": True,
        "lazy": True,
        "worker": "maplibre-gl-csp-worker.js",
        "public_python_type": False,
    }
    csp = {
        "script-src": "'self'",
        "worker-src": "'self'",
        "connect-src": " ".join(["'self'", *origins]) if origins else "'self'",
        "img-src": " ".join(["'self'", "data:", *origins]) if origins else "'self' data:",
        "style-src": "'self'",
    }
    accessibility = AccessibilityPlan(
        title=parsed.accessibility.title,
        description=parsed.accessibility.description,
        include_table=parsed.accessibility.include_table,
        decorative=parsed.accessibility.decorative,
        table_rows=rows,
    )
    fallback = {
        "title": parsed.accessibility.title,
        "description": parsed.accessibility.description,
        "alternative_class": "hedron-map-alternative",
        "table_rows": list(rows),
        "actions": "ordinary links and buttons without JavaScript",
    }
    view = parsed.view
    bounds = None
    if view.fit == "layers" and rows:
        lats = [float(row["lat"]) for row in rows if row.get("lat") is not None]
        lons = [float(row["lon"]) for row in rows if row.get("lon") is not None]
        if lats and lons:
            bounds = Bounds(west=min(lons), south=min(lats), east=max(lons), north=max(lats))
    redacted = {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "renderer": renderer,
        "resources": resources,
        "origins": origins,
        "attribution": attribution,
        "view": view.model_dump(mode="json"),
        "layers": compiled_layers,
        "style": style,
        "source_kind": kind,
        "preset_id": preset,
        "accessibility": accessibility.model_dump(mode="json"),
    }
    if _byte_size(redacted) > MAX_PLAN_BYTES:
        raise _map_error(
            HED_MAP_SPEC_0002,
            "Plan byte budget exceeded",
            f"Compiled plan exceeds {MAX_PLAN_BYTES} bytes.",
            "Reduce GeoJSON, style, or overlay cardinality.",
        )
    plan = MapPlan(
        spec_fingerprint=_fingerprint(parsed.to_json_dict()),
        plan_fingerprint=_fingerprint(redacted),
        renderer=renderer,
        resources=tuple(resources),
        origins=tuple(origins),
        csp=csp,
        attribution=tuple(dict.fromkeys(attribution)),
        fallback=fallback,
        bounds=bounds,
        view=view,
        layers=compiled_layers,
        style=style,
        limits=dict(LIMITS),
        warnings=tuple(warnings),
        accessibility=accessibility,
        events=(
            "feature-selected",
            "feature-activated",
            "viewport-changed",
            "layer-visibility-changed",
            "map-loaded",
            "map-failed",
        ),
        source_kind=kind,  # type: ignore[arg-type]
        preset_id=preset,
    )
    _reject_pollution(plan.to_json_dict())
    encoded = json.dumps(plan.to_json_dict(), separators=(",", ":"))
    if "Bearer " in encoded or "userinfo" in encoded.lower():
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Plan redaction failed",
            "Compiled JSON still contained credential-shaped content.",
            "Do not place secrets in MapSpec fields.",
        )
    return plan
