"""CSP-safe host element rendering for optional chart adapters."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

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
    payload: Mapping[str, Any] | str
    if isinstance(output.body, str):
        try:
            parsed = json.loads(output.body)
            payload = parsed if isinstance(parsed, Mapping) else {"body": parsed}
        except json.JSONDecodeError:
            payload = {"body": output.body}
    elif isinstance(output.body, Mapping):
        payload = dict(output.body)
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
    if not rows:
        return Text("")
    return html.div(
        html.p("Tabular fallback"),
        class_="hedron-chart-fallback",
    )


def extract_folium_payload(value: object) -> dict[str, Any]:
    """Extract CSP-safe map center/zoom/markers from a Folium map or mapping."""
    if isinstance(value, Mapping):
        if value.get("type") == "folium" or "center" in value or "location" in value:
            center = value.get("center") or value.get("location") or [0.0, 0.0]
            return {
                "center": list(center) if not isinstance(center, list) else center,
                "zoom": int(value.get("zoom") or 2),
                "geojson": value.get("geojson"),
                "markers": list(value.get("markers") or []),
                "style": value.get("style") or "basic",
            }
        raise TypeError("Folium mapping requires center/location or type=folium")

    location = getattr(value, "location", None)
    zoom = getattr(value, "zoom_start", None) or getattr(value, "zoom", None) or 2
    markers: list[dict[str, Any]] = []
    geojson: object | None = None
    children = getattr(value, "_children", None)
    if isinstance(children, Mapping):
        for child in children.values():
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
        "zoom": int(zoom),
        "markers": markers,
        "geojson": geojson,
        "style": "basic",
    }


def downsample_plotly_body(body: Mapping[str, Any], *, max_points: int) -> dict[str, Any]:
    """Downsample Plotly-like data arrays to ``max_points`` (stride sample)."""
    out = dict(body)
    data = out.get("data")
    if not isinstance(data, list):
        # Accept flat x/y arrays on the body itself.
        for key in ("x", "y"):
            seq = out.get(key)
            if isinstance(seq, list) and len(seq) > max_points:
                step = max(1, len(seq) // max_points)
                out[key] = seq[::step][:max_points]
        out["max_points"] = max_points
        out["resampled"] = True
        return out
    new_data = []
    for trace in data:
        if not isinstance(trace, Mapping):
            new_data.append(trace)
            continue
        t = dict(trace)
        for key in ("x", "y", "z", "lat", "lon"):
            seq = t.get(key)
            if isinstance(seq, list) and len(seq) > max_points:
                step = max(1, len(seq) // max_points)
                t[key] = seq[::step][:max_points]
        new_data.append(t)
    out["data"] = new_data
    out["max_points"] = max_points
    out["resampled"] = True
    return out
