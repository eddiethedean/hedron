"""MapSpec → MapPlan compiler (SPEC-047 / PROVIDER-047). No I/O."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import cast
from urllib.parse import urlparse

from typing_extensions import TypeIs

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
from hedron_core.typing_aliases import JsonObject, JsonValue
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
    SourceKind,
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
        mapping = cast(Mapping[object, object], obj)
        for key, value in mapping.items():
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
        sequence = cast(Sequence[object], obj)
        for index, item in enumerate(sequence):
            _reject_pollution(item, f"{path}[{index}]")


def _reject_nonfinite(obj: object, path: str = "$") -> None:
    if isinstance(obj, float) and not math.isfinite(obj):
        raise _map_error(
            HED_MAP_SPEC_0001,
            "Invalid MapSpec numeric value",
            f"Non-finite numeric value at {path} is not valid JSON.",
            "Replace NaN and infinity with finite values or null.",
        )
    if isinstance(obj, Mapping):
        for key, value in cast(Mapping[object, object], obj).items():
            _reject_nonfinite(value, f"{path}.{key}")
    elif isinstance(obj, (list, tuple)):
        for index, item in enumerate(cast(Sequence[object], obj)):
            _reject_nonfinite(item, f"{path}[{index}]")


def _byte_size(payload: object) -> int:
    return len(
        json.dumps(payload, default=str, separators=(",", ":"), allow_nan=False).encode("utf-8")
    )


def parse_map_spec(raw: MapSpec | Mapping[str, object]) -> MapSpec:
    if isinstance(raw, MapSpec):
        _reject_nonfinite(raw.model_dump(mode="python"))
        _reject_pollution(raw.to_json_dict())
        return raw
    _reject_pollution(raw)
    _reject_nonfinite(raw)
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
    try:
        parsed = urlparse(url)
        _port = parsed.port  # Force deferred malformed-port validation.
    except ValueError as exc:
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Malformed URL host or port",
            f"Could not parse {url!r}: {exc}",
            "Use a valid HTTPS URL with a port from 0 through 65535.",
        ) from exc
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None


def _validate_url(url: str, *, allow_relative: bool = True) -> str:
    if url != url.strip() or any(ord(ch) < 32 or ord(ch) == 127 or ch.isspace() for ch in url):
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Unsafe URL rejected",
            f"Refused {url!r}.",
            "Use a canonical HTTPS or same-origin path without whitespace or controls.",
        )
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
    try:
        parsed = urlparse(url)
        # urllib defers malformed-port validation until ``.port`` is read.
        _port = parsed.port
    except ValueError as exc:
        raise _map_error(
            HED_MAP_POLICY_0002,
            "Malformed URL host or port",
            f"Could not parse {url!r}: {exc}",
            "Use a valid HTTPS URL with a port from 0 through 65535.",
        ) from exc
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
    if parsed.scheme == "https" and (not parsed.netloc or not parsed.hostname):
        raise _map_error(
            HED_MAP_POLICY_0002,
            "HTTPS resource host missing",
            f"Refused malformed absolute URL {url!r}.",
            "Use https:// followed by an explicit host.",
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
    if not policy.remote_requests_permitted:
        raise _map_error(
            HED_MAP_POLICY_0001,
            "Remote map requests are not permitted",
            f"{origin} requires a remote fetch while remote_requests_permitted is false.",
            "Set remote_requests_permitted=True or use same-origin /assets paths.",
        )
    allowed = tuple(policy.allowed_origins)
    if origin not in allowed:
        raise _map_error(
            HED_MAP_POLICY_0001,
            "Origin not in MapPolicy.allowed_origins",
            f"{origin} is not an exact allowed origin.",
            "Add the exact HTTPS origin to MapPolicy(allowed_origins=...).",
        )


def _is_json_value(value: object) -> TypeIs[JsonValue]:
    if value is None or isinstance(value, (str, int, float, bool)):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in cast(list[object], value))
    if isinstance(value, dict):
        items = cast(dict[object, object], value)
        return all(isinstance(key, str) and _is_json_value(item) for key, item in items.items())
    return False


def _as_json(value: object) -> JsonValue:
    if _is_json_value(value):
        return value
    # Compiler-internal dumps are JSON-shaped; stringify unknown leaves.
    return str(value)


def _as_json_object(value: object) -> JsonObject:
    if isinstance(value, dict) and all(
        isinstance(key, str) and _is_json_value(item)
        for key, item in cast(dict[object, object], value).items()
    ):
        return cast(JsonObject, value)
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        return {str(key): _as_json(item) for key, item in mapping.items()}
    return {}


def _as_object_dict(value: Mapping[str, object]) -> dict[str, object]:
    return {str(key): item for key, item in value.items()}


def _as_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            number = float(value)
        except OverflowError:
            return None
        return number if math.isfinite(number) else None
    if isinstance(value, str):
        try:
            number = float(value)
        except (ValueError, OverflowError):
            return None
        return number if math.isfinite(number) else None
    return None


def _iter_json_array(value: object) -> Sequence[object]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return cast(Sequence[object], value)
    return ()


def _ensure_style_object(style: JsonObject, key: str, default: JsonValue) -> JsonValue:
    value = style.get(key)
    if value is None:
        style[key] = default
        return default
    return value


def _style_sources(style: JsonObject) -> JsonObject:
    sources = _ensure_style_object(style, "sources", {})
    if isinstance(sources, dict):
        return _as_json_object(sources)
    empty: JsonObject = {}
    style["sources"] = empty
    return empty


def _set_basemap_raster(
    style: JsonObject,
    *,
    tiles: Sequence[str],
    attribution: str,
    extra: Mapping[str, JsonValue] | None = None,
) -> None:
    source: JsonObject = {
        "type": "raster",
        "tiles": list(tiles),
        "attribution": attribution,
    }
    if extra:
        source.update(dict(extra))
    _style_sources(style)["basemap"] = source
    style["layers"] = [{"id": "basemap", "type": "raster", "source": "basemap"}]


def _reject_remote_origins(origins: Sequence[str], policy: MapPolicy) -> None:
    if policy.remote_requests_permitted or not origins:
        return
    raise _map_error(
        HED_MAP_POLICY_0001,
        "Remote map requests are not permitted",
        f"Compiled remote origins {tuple(origins)} while remote_requests_permitted is false.",
        "Set remote_requests_permitted=True or use same-origin /assets paths.",
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
        sequence = cast(Sequence[object], obj)
        if sequence and all(isinstance(item, (int, float)) for item in sequence):
            return 1
        return sum(_count_coords(item, depth=depth + 1) for item in sequence)
    return 0


def _layer_geojson(layer: Layer) -> Mapping[str, object] | None:
    data = getattr(layer, "data", None)
    return cast(Mapping[str, object], data) if isinstance(data, Mapping) else None


def _sanitize_layer(layer: Layer, *, max_features: int) -> JsonObject:
    dumped = _as_json_object(layer.model_dump(mode="json"))
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
    style: MapStyle | Mapping[str, object] | None, *, origins: list[str], policy: MapPolicy
) -> JsonObject:
    if style is None:
        return {"version": 8, "sources": {}, "layers": []}
    dumped = (
        _as_json_object(style.model_dump(mode="json"))
        if isinstance(style, MapStyle)
        else _as_json_object(dict(style))
    )
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
    for layer in _iter_json_array(dumped.get("layers")):
        layer_type: object = None
        if isinstance(layer, Mapping):
            layer_type = cast(Mapping[object, object], layer).get("type")
        if isinstance(layer, Mapping) and layer_type not in ALLOWED_STYLE_LAYER_TYPES:
            raise _map_error(
                HED_MAP_STYLE_0001,
                "Unsupported style layer type",
                f"Layer type {layer_type!r} is outside the locked subset.",
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
    sources = dumped.get("sources")
    if isinstance(sources, dict):
        dumped["sources"] = {
            str(key): _close_style_source(source, origins=origins, policy=policy)
            for key, source in sources.items()
        }
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


def _close_style_url(url: str, *, origins: list[str], policy: MapPolicy) -> str:
    checked = _validate_url(url)
    origin = _origin_of(checked)
    if origin:
        _policy_allows(origin, policy, local=False)
        if origin not in origins:
            origins.append(origin)
    return checked


def _close_style_source(source: object, *, origins: list[str], policy: MapPolicy) -> JsonValue:
    if not isinstance(source, Mapping):
        return _as_json(source)
    mapping = cast(Mapping[object, object], source)
    closed: JsonObject = {str(key): _as_json(value) for key, value in mapping.items()}
    tiles = closed.get("tiles")
    if isinstance(tiles, Sequence) and not isinstance(tiles, (str, bytes)):
        closed["tiles"] = [
            _close_style_url(tile, origins=origins, policy=policy)
            if isinstance(tile, str)
            else _as_json(tile)
            for tile in tiles
        ]
    for field in ("url", "data"):
        value = closed.get(field)
        if isinstance(value, str) and value and not value.lstrip().startswith(("{", "[")):
            closed[field] = _close_style_url(value, origins=origins, policy=policy)
    urls = closed.get("urls")
    if isinstance(urls, Sequence) and not isinstance(urls, (str, bytes)):
        closed["urls"] = [
            _close_style_url(item, origins=origins, policy=policy)
            if isinstance(item, str)
            else _as_json(item)
            for item in urls
        ]
    return closed


def _basemap_facts(
    spec: MapSpec,
    policy: MapPolicy,
) -> tuple[SourceKind, str | None, list[str], list[str], list[str], JsonObject, list[str]]:
    """Return kind, preset id, resources, origins, attribution, style, warnings."""
    basemap = spec.basemap
    warnings: list[str] = []
    origins: list[str] = []
    resources: list[str] = []
    attribution: list[str] = []
    style: JsonObject = {"version": 8, "sources": {}, "layers": []}

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
        origin = _origin_of(basemap.tile_url)
        if origin is None:
            # Relative / local templates are not the public OSM CDN.
            _policy_allows(None, policy, local=True)
            resources.append(basemap.tile_url)
            _set_basemap_raster(
                style,
                tiles=[basemap.tile_url],
                attribution=attr,
                extra={"tileSize": basemap.tile_size},
            )
            warnings.append(
                "OSM-compatible local tile_url has no remote origin; "
                "standard OSM CDN origin was not inferred."
            )
            return basemap.kind, OSM_STANDARD_ID, resources, origins, attribution, style, warnings
        if origin != OSM_STANDARD_ORIGIN or (
            policy.allowed_origins and origin not in policy.allowed_origins
        ):
            _policy_allows(origin, policy, local=False)
        origins.append(origin)
        resources.append(basemap.tile_url)
        _set_basemap_raster(
            style,
            tiles=[basemap.tile_url],
            attribution=attr,
            extra={"tileSize": basemap.tile_size},
        )
        warnings.append("OSM standard preset is replaceable and has no availability/SLA claim.")
        return basemap.kind, OSM_STANDARD_ID, resources, origins, attribution, style, warnings

    if isinstance(basemap, RasterTiles):
        _validate_template(basemap.url, scale=basemap.scale, subdomain=basemap.subdomain)
        _zoom_ok(basemap.min_zoom, basemap.max_zoom)
        origin = _origin_of(basemap.url)
        _policy_allows(origin, policy, local=origin is None)
        if origin:
            origins.append(origin)
        resources.append(basemap.url)
        _set_basemap_raster(
            style,
            tiles=[basemap.url],
            attribution=attr,
            extra={"tileSize": basemap.tile_size, "scheme": basemap.scheme},
        )
        return basemap.kind, None, resources, origins, attribution, style, warnings

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
            tiles = basemap.document.get("tiles")
            if isinstance(tiles, Sequence) and not isinstance(tiles, (str, bytes)):
                tile_values = cast(Sequence[object], tiles)
                for tile in tile_values:
                    if isinstance(tile, str):
                        _validate_url(tile)
                        origin = _origin_of(tile)
                        _policy_allows(origin, policy, local=origin is None)
                        if origin and origin not in origins:
                            origins.append(origin)
                        resources.append(tile)
                tile_urls = [tile for tile in tile_values if isinstance(tile, str)]
                if tile_urls:
                    source_type = "raster"
                    declared = str(basemap.document.get("type") or "raster")
                    if declared in {"raster", "vector"}:
                        source_type = declared
                    _style_sources(style)["basemap"] = _as_json(
                        {
                            "type": source_type,
                            "tiles": tile_urls,
                            "attribution": attr,
                        }
                    )
                    layer_type = "raster" if source_type == "raster" else "circle"
                    style["layers"] = [{"id": "basemap", "type": layer_type, "source": "basemap"}]
        if basemap.url:
            checked = _validate_url(basemap.url)
            origin = _origin_of(checked)
            _policy_allows(origin, policy, local=origin is None)
            if origin:
                origins.append(origin)
            resources.append(checked)
            sources = _style_sources(style)
            if "basemap" not in sources:
                sources["basemap"] = _as_json(
                    {
                        "type": "raster",
                        "url": checked,
                        "attribution": attr,
                    }
                )
                style["layers"] = [{"id": "basemap", "type": "raster", "source": "basemap"}]
        return basemap.kind, None, resources, origins, attribution, style, warnings

    if isinstance(basemap, VectorTiles):
        _validate_template(basemap.url, scale=None, subdomain=None)
        _zoom_ok(basemap.min_zoom, basemap.max_zoom)
        origin = _origin_of(basemap.url)
        _policy_allows(origin, policy, local=origin is None)
        if origin:
            origins.append(origin)
        resources.append(basemap.url)
        style = _style_subset(basemap.style, origins=origins, policy=policy)
        _style_sources(style)["basemap"] = _as_json(
            {
                "type": "vector",
                "tiles": [basemap.url],
                "attribution": attr,
            }
        )
        return basemap.kind, None, resources, origins, attribution, style, warnings

    if isinstance(basemap, StaticImage):
        checked = _validate_url(basemap.src)
        origin = _origin_of(checked)
        if origin:
            _policy_allows(origin, policy, local=False)
            origins.append(origin)
        resources.append(checked)
        coordinates: list[list[float]] = [
            [-180.0, 85.0],
            [180.0, 85.0],
            [180.0, -85.0],
            [-180.0, -85.0],
        ]
        if basemap.bounds is not None:
            west, south, east, north = basemap.bounds
            coordinates = [[west, north], [east, north], [east, south], [west, south]]
        _style_sources(style)["basemap"] = _as_json(
            {
                "type": "image",
                "url": checked,
                "coordinates": coordinates,
            }
        )
        style["layers"] = [{"id": "basemap", "type": "raster", "source": "basemap"}]
        return basemap.kind, None, resources, origins, attribution, style, warnings

    if isinstance(basemap, PMTiles):
        checked = _validate_url(basemap.src)
        origin = _origin_of(checked)
        if origin:
            _policy_allows(origin, policy, local=False)
            origins.append(origin)
        resources.append(checked)
        source_type = "vector" if basemap.vector else "raster"
        _style_sources(style)["basemap"] = _as_json(
            {
                "type": source_type,
                "url": checked,
                "attribution": attr,
            }
        )
        style["layers"] = [
            {
                "id": "basemap",
                "type": "circle" if source_type == "vector" else "raster",
                "source": "basemap",
            }
        ]
        if basemap.style:
            style_url = _validate_url(basemap.style)
            style_origin = _origin_of(style_url)
            if style_origin:
                _policy_allows(style_origin, policy, local=False)
                if style_origin not in origins:
                    origins.append(style_origin)
            resources.append(style_url)
        return basemap.kind, None, resources, origins, attribution, style, warnings

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
        route = basemap.route_template.replace("{archive_id}", basemap.archive_id)
        _set_basemap_raster(
            style,
            tiles=[route],
            attribution=attr,
            extra={"minzoom": basemap.min_zoom, "maxzoom": basemap.max_zoom},
        )
        return basemap.kind, None, resources, origins, attribution, style, warnings

    if isinstance(basemap, NoBasemap):  # pyright: ignore[reportUnnecessaryIsInstance]
        return basemap.kind, None, resources, origins, attribution, style, warnings

    if isinstance(basemap, OfflineMapBundle):  # pyright: ignore[reportUnnecessaryIsInstance]
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
        archive = getattr(basemap, "archive_or_image", None)
        sources = _style_sources(style)
        if isinstance(archive, str) and archive and "basemap" not in sources:
            sources["basemap"] = _as_json(
                {
                    "type": "raster",
                    "url": archive,
                    "attribution": attr or str(basemap.attribution or ""),
                }
            )
            style["layers"] = [{"id": "basemap", "type": "raster", "source": "basemap"}]
        if basemap.attribution:
            attribution.append(basemap.attribution)
        return "pmtiles", None, resources, origins, attribution, style, warnings

    raise _map_error(
        HED_MAP_SOURCE_0002,
        "Unknown basemap type",
        f"Unsupported basemap {type(basemap).__name__}.",
        "Use a Supported catalog source kind.",
    )


def _apply_overlay_style(
    style: JsonObject, compiled_layers: Sequence[Mapping[str, JsonValue]]
) -> None:
    """Fold compiled overlay layers into the MapLibre style the host mounts."""
    sources = _style_sources(style)
    layers_value = _ensure_style_object(style, "layers", [])
    if not isinstance(layers_value, list):
        return
    layers: list[JsonValue] = [_as_json(item) for item in layers_value]
    style["layers"] = layers
    for index, layer in enumerate(compiled_layers):
        kind = str(layer.get("kind") or "")
        source_id = f"overlay-{index}"
        if kind == "marker":
            features: list[JsonValue] = []
            for marker in _iter_json_array(layer.get("markers")):
                if not isinstance(marker, Mapping):
                    continue
                marker_mapping = cast(Mapping[object, object], marker)
                features.append(
                    {
                        "type": "Feature",
                        "id": _as_json(marker_mapping.get("id")),
                        "properties": {
                            "id": _as_json(marker_mapping.get("id")),
                            "name": _as_json(marker_mapping.get("label")),
                            "label": _as_json(marker_mapping.get("label")),
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                _as_json(marker_mapping.get("lon")),
                                _as_json(marker_mapping.get("lat")),
                            ],
                        },
                    }
                )
            sources[source_id] = {
                "type": "geojson",
                "data": {"type": "FeatureCollection", "features": features},
            }
            layers.append({"id": source_id, "type": "circle", "source": source_id})
        elif kind in {"geojson", "line", "polygon", "circle"}:
            data = layer.get("data") or {"type": "FeatureCollection", "features": []}
            sources[source_id] = {"type": "geojson", "data": _as_json(data)}
            paint_value = layer.get("paint")
            paint = paint_value if isinstance(paint_value, dict) else None
            if kind == "geojson":
                layers.append(
                    {
                        "id": f"{source_id}-fill",
                        "type": "fill",
                        "source": source_id,
                        "filter": ["==", ["geometry-type"], "Polygon"],
                    }
                )
                layers.append({"id": f"{source_id}-line", "type": "line", "source": source_id})
                layers.append(
                    {
                        "id": f"{source_id}-circle",
                        "type": "circle",
                        "source": source_id,
                        "filter": ["==", ["geometry-type"], "Point"],
                    }
                )
            else:
                layer_type = {"line": "line", "polygon": "fill", "circle": "circle"}[kind]
                entry: JsonObject = {
                    "id": source_id,
                    "type": layer_type,
                    "source": source_id,
                }
                if paint is not None:
                    entry["paint"] = {str(key): _as_json(value) for key, value in paint.items()}
                layers.append(entry)
        elif kind == "raster":
            raster_source = str(layer.get("source") or "basemap")
            layers.append({"id": source_id, "type": "raster", "source": raster_source})


def _fallback_rows(spec: MapSpec, _layers: Sequence[JsonObject]) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
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
            props = feature.get("properties")
            label = ""
            if isinstance(props, Mapping):
                for key in ("name", "title", "label", "id"):
                    value = props.get(key)
                    if isinstance(value, str) and value.strip():
                        label = value
                        break
            geometry = feature.get("geometry")
            lat: object = None
            lon: object = None
            if isinstance(geometry, Mapping) and geometry.get("type") == "Point":
                coords = geometry.get("coordinates")
                if (
                    isinstance(coords, Sequence)
                    and not isinstance(coords, (str, bytes))
                    and len(coords) >= 2
                ):
                    lon, lat = coords[0], coords[1]
            rows.append(
                {"id": str(feature.get("id", index)), "label": label, "lat": lat, "lon": lon}
            )
    return tuple(rows[:MAX_FEATURES])


def compile_map(
    spec: MapSpec | Mapping[str, object],
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
        if origin == OSM_STANDARD_ORIGIN:
            resolved_policy = MapPolicy(
                allowed_origins=(OSM_STANDARD_ORIGIN,),
                allowed_source_kinds=effective.allowed_source_kinds,
                remote_requests_permitted=effective.remote_requests_permitted,
                allow_proxy=effective.allow_proxy,
            )
        else:
            # Relative / custom hosts keep the caller's policy (no forged OSM origin).
            resolved_policy = effective
        kind, preset, resources, origins, attribution, style, warnings = _basemap_facts(
            parsed, resolved_policy
        )
    else:
        resolved_policy = effective
        kind, preset, resources, origins, attribution, style, warnings = _basemap_facts(
            parsed, resolved_policy
        )

    _reject_remote_origins(origins, resolved_policy)

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
            sanitized: list[JsonValue] = []
            for item in _iter_json_array(marker.get("markers")):
                if not isinstance(item, Mapping):
                    continue
                item_mapping = cast(Mapping[object, object], item)
                if item_mapping.get("action") and item_mapping.get("href"):
                    raise _map_error(
                        HED_MAP_0004,
                        "Marker cannot mix href and action",
                        "Reuse HED-MAP-0004 semantics: one ordinary action path per marker.",
                        "Supply href or action, not both.",
                    )
                marker_spec = MarkerSpec.model_validate(
                    {
                        "id": str(item_mapping.get("id") or "marker"),
                        "lat": item_mapping.get("lat"),
                        "lon": item_mapping.get("lon"),
                        "label": str(item_mapping.get("label") or ""),
                        "href": item_mapping.get("href"),
                        "action": item_mapping.get("action"),
                    }
                )
                sanitized.append(
                    {
                        "id": marker_spec.id,
                        "lat": marker_spec.lat,
                        "lon": marker_spec.lon,
                        "label": marker_spec.label,
                        "href": (str(marker_spec.href) if marker_spec.href is not None else None),
                        "action": marker_spec.action,
                    }
                )
            marker["markers"] = sanitized

    _apply_overlay_style(style, compiled_layers)

    renderer: JsonObject = {
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
    fallback: dict[str, object] = {
        "title": parsed.accessibility.title,
        "description": parsed.accessibility.description,
        "alternative_class": "hedron-map-alternative",
        "table_rows": list(rows),
        "actions": "ordinary links and buttons without JavaScript",
    }
    view = parsed.view
    bounds = None
    if view.fit == "layers" and rows:
        lats = [lat for row in rows if (lat := _as_float(row.get("lat"))) is not None]
        lons = [lon for row in rows if (lon := _as_float(row.get("lon"))) is not None]
        if lats and lons:
            bounds = Bounds(west=min(lons), south=min(lats), east=max(lons), north=max(lats))
    redacted: JsonObject = {
        "schema_id": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "renderer": renderer,
        "resources": list(resources),
        "origins": list(origins),
        "attribution": list(attribution),
        "view": _as_json(view.model_dump(mode="json")),
        "layers": list(compiled_layers),
        "style": style,
        "source_kind": kind,
        "preset_id": preset,
        "accessibility": _as_json(accessibility.model_dump(mode="json")),
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
        renderer=_as_object_dict(renderer),
        resources=tuple(resources),
        origins=tuple(origins),
        csp=csp,
        attribution=tuple(dict.fromkeys(attribution)),
        fallback=fallback,
        bounds=bounds,
        view=view,
        layers=tuple(_as_object_dict(layer) for layer in compiled_layers),
        style=_as_object_dict(style),
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
        source_kind=kind,
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
