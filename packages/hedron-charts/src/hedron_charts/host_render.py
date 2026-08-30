"""CSP-safe host element rendering for optional chart adapters."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any, cast

from hedron_core.builtins.content import Text
from hedron_core.component import NodeLike
from hedron_core.html import html
from hedron_core.visualization import ChartOutput


def render_host_figure(
    output: ChartOutput,
    *,
    host: str,
    class_suffix: str | None = None,
) -> NodeLike:
    """Render a figure with a custom element carrying non-executable JSON payload."""
    acc = output.accessibility
    payload: Mapping[str, Any]
    if isinstance(output.body, str):
        try:
            parsed = json.loads(output.body)
            payload = (
                cast(Mapping[str, Any], parsed) if isinstance(parsed, Mapping) else {"body": parsed}
            )
        except json.JSONDecodeError:
            payload = {"body": output.body}
    elif isinstance(output.body, Mapping):
        body_mapping = cast(Mapping[object, object], output.body)
        payload = {str(key): value for key, value in body_mapping.items()}
    else:
        payload = {"body": str(output.body)}
    wrapped = {
        "spec": payload,
        "kind": output.kind,
        "adapter": (output.metadata or {}).get("adapter"),
        "accessibility": {
            "title": acc.title,
            "description": acc.description,
            "alt": acc.alt,
        },
    }
    raw = json.dumps(wrapped, default=str)
    suffix = class_suffix or host
    attrs: dict[str, str] = {
        "data-hedron-chart": host,
        "data-hedron-payload": raw,
        "role": "img",
        "aria-label": acc.alt or acc.title,
    }
    return html.figure(
        html.h2(acc.title),
        html.p(acc.description or acc.alt or ""),
        html.div(**attrs),
        _tabular(acc.tabular_fallback),
        class_=f"hedron-chart hedron-chart-{suffix}",
    )


def _tabular(rows: object) -> NodeLike:
    from hedron_charts.adapters import _fallback_table  # pyright: ignore[reportPrivateUsage]

    if not rows:
        return Text("")
    if isinstance(rows, Sequence) and not isinstance(rows, (str, bytes)):
        typed_rows = cast(Sequence[object], rows)
        cleaned: list[Mapping[str, Any]] = [
            cast(Mapping[str, Any], row) for row in typed_rows if isinstance(row, Mapping)
        ]
        return _fallback_table(cleaned)
    return Text("")


def _coerce_zoom(raw: object, *, default: int = 2) -> int:
    """Preserve explicit zoom 0; default only when absent/None (#118)."""
    if raw is None:
        return default
    if isinstance(raw, bool):
        raise ValueError("zoom must be a numeric level, not a boolean")
    try:
        zoom = int(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid zoom value {raw!r}") from exc
    if zoom < 0 or zoom > 22:
        raise ValueError(f"zoom out of range: {zoom}")
    return zoom


def extract_folium_payload(value: object) -> dict[str, Any]:
    """Extract CSP-safe map center/zoom/markers from a Folium map or mapping."""
    if isinstance(value, Mapping):
        mapping = cast(Mapping[str, Any], value)
        if mapping.get("type") == "folium" or "center" in mapping or "location" in mapping:
            center = mapping.get("center") or mapping.get("location") or [0.0, 0.0]
            zoom_raw = mapping.get("zoom")
            return {
                "center": list(center) if not isinstance(center, list) else center,
                "zoom": _coerce_zoom(zoom_raw),
                "geojson": mapping.get("geojson"),
                "markers": list(mapping.get("markers") or []),
                "style": mapping.get("style") or "basic",
                "coord_order": mapping.get("coord_order") or "latlng",
            }
        raise TypeError("Folium mapping requires center/location or type=folium")

    location = getattr(value, "location", None)
    zoom_raw = getattr(value, "zoom_start", None)
    if zoom_raw is None:
        zoom_raw = getattr(value, "zoom", None)
    markers: list[dict[str, Any]] = []
    geojson: object | None = None
    children = getattr(value, "_children", None)
    if isinstance(children, Mapping):
        child_mapping = cast(Mapping[object, Any], children)
        for child in child_mapping.values():
            mod = type(child).__module__
            name = type(child).__name__.lower()
            if "marker" in name:
                loc = getattr(child, "location", None)
                popup = getattr(child, "popup", None)
                markers.append(
                    {
                        "location": list(loc) if loc is not None else None,
                        "popup": str(getattr(popup, "html", popup) or ""),
                    }
                )
            if "geojson" in name or "geojson" in mod:
                data = getattr(child, "data", None)
                if data is not None:
                    geojson = data
    if location is None:
        location = [0.0, 0.0]
    return {
        "center": list(location),
        "zoom": _coerce_zoom(zoom_raw),
        "markers": markers,
        "geojson": geojson,
        "style": "basic",
        "coord_order": "latlng",
    }


def extract_pydeck_payload(value: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize PyDeck / deck.gl JSON to the Folium-shaped MapLibre host contract (#84)."""
    if "center" in value and "zoom" in value and "initial_view_state" not in value:
        # Already MapLibre/Folium-shaped.
        center = value["center"]
        return {
            "center": list(center) if not isinstance(center, list) else center,
            "zoom": _coerce_zoom(value.get("zoom")),
            "geojson": value.get("geojson"),
            "markers": list(value.get("markers") or []),
            "style": value.get("style") or "basic",
            "coord_order": value.get("coord_order") or "latlng",
        }

    view_value: object = value.get("initial_view_state") or value.get("view_state") or {}
    if not isinstance(view_value, Mapping):
        raise TypeError("PyDeck payload requires initial_view_state mapping")
    view = cast(Mapping[str, Any], view_value)

    lat = view.get("latitude")
    lng = view.get("longitude")
    if lat is None or lng is None:
        raise TypeError("PyDeck initial_view_state requires latitude and longitude")
    center = [float(lat), float(lng)]
    zoom = _coerce_zoom(view.get("zoom"))

    layers_value: object = value.get("layers")
    if layers_value is None:
        layers: Sequence[Any] = ()
    elif isinstance(layers_value, Sequence) and not isinstance(
        layers_value, (str, bytes, bytearray)
    ):
        layers = cast(Sequence[Any], layers_value)
    else:
        raise TypeError("PyDeck layers must be a sequence of layer mappings")
    markers_value: object = value.get("markers") or []
    markers: list[dict[str, Any]] = (
        list(cast(Sequence[dict[str, Any]], markers_value))
        if isinstance(markers_value, Sequence) and not isinstance(markers_value, (str, bytes))
        else []
    )
    geojson: object | None = value.get("geojson")
    if layers:
        converted = False
        for layer in layers:
            if not isinstance(layer, Mapping):
                raise TypeError(
                    "PyDeck layers cannot be rendered by the MapLibre host; "
                    "pass Folium-shaped center/zoom/markers/geojson instead."
                )
            layer_mapping = cast(Mapping[str, Any], layer)
            data = layer_mapping.get("data")
            # Accept simple point lists as markers; anything else is unsupported.
            data_points = cast(list[Any], data) if isinstance(data, list) else []
            if data_points and all(
                isinstance(pt, (list, tuple)) and len(cast(Sequence[object], pt)) >= 2
                for pt in data_points
            ):
                for pt in data_points:
                    point = cast(Sequence[Any], pt)
                    markers.append({"location": [float(point[1]), float(point[0])]})
                converted = True
            elif isinstance(data, Mapping) and cast(Mapping[str, Any], data).get("type") in {
                "FeatureCollection",
                "Feature",
                "GeometryCollection",
            }:
                geojson = cast(object, data)
                converted = True
            elif data in (None, [], {}):
                converted = True
            else:
                raise TypeError(
                    "Unsupported PyDeck layer for MapLibre host; "
                    "convert to markers/geojson or omit layers."
                )
        if not converted and layers:
            raise TypeError("Unsupported PyDeck layers for MapLibre host")

    return {
        "center": center,
        "zoom": zoom,
        "markers": markers,
        "geojson": geojson,
        "style": value.get("style") or "basic",
        "coord_order": value.get("coord_order") or "latlng",
    }


def downsample_plotly_body(body: Mapping[str, Any], *, max_points: int) -> dict[str, Any]:
    """Downsample Plotly-like data arrays to ``max_points`` (stride sample).

    ``max_points`` must be a positive integer (#83); non-positive values fail closed.
    """
    if (
        not isinstance(max_points, int)  # pyright: ignore[reportUnnecessaryIsInstance]
        or isinstance(max_points, bool)
        or max_points < 1
    ):
        raise ValueError("max_points must be a positive integer")
    out = dict(body)
    data = out.get("data")
    if not isinstance(data, list):
        # Accept flat x/y arrays on the body itself.
        for key in ("x", "y"):
            seq_value = out.get(key)
            if isinstance(seq_value, list):
                seq = cast(list[Any], seq_value)
                if len(seq) <= max_points:
                    continue
                step = max(1, len(seq) // max_points)
                out[key] = seq[::step][:max_points]
        out["max_points"] = max_points
        out["resampled"] = True
        return out
    traces = cast(list[Any], data)
    new_data: list[Any] = []
    for trace in traces:
        if not isinstance(trace, Mapping):
            new_data.append(trace)
            continue
        t = dict(cast(Mapping[str, Any], trace))
        for key in ("x", "y", "z", "lat", "lon"):
            seq_value = t.get(key)
            if isinstance(seq_value, list):
                seq = cast(list[Any], seq_value)
                if len(seq) <= max_points:
                    continue
                step = max(1, len(seq) // max_points)
                t[key] = seq[::step][:max_points]
        new_data.append(t)
    out["data"] = new_data
    out["max_points"] = max_points
    out["resampled"] = True
    return out
