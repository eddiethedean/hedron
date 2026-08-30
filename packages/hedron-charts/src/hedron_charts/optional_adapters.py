"""Optional visualization adapters for phase 0.12 scale."""

from __future__ import annotations

import importlib
import json
import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any, cast
from urllib.parse import unquote

from hedron_charts.host_render import (
    downsample_plotly_body,
    extract_folium_payload,
    extract_pydeck_payload,
    render_host_figure,
)
from hedron_charts.limits import (
    ensure_limits,
    missing_extra,
    payload_size,
    redact_rows,
    reject_active_svg,
    reject_callbacks,
    reject_remote_urls,
)
from hedron_core.component import NodeLike
from hedron_core.diagnostics import error
from hedron_core.html import html
from hedron_core.security import TrustedHtml
from hedron_core.visualization import ChartAccessibility, ChartOutput, VisualizationLimits

__all__ = [
    "BokehAdapter",
    "ChartJsAdapter",
    "DatashaderAdapter",
    "EChartsAdapter",
    "EXPERIMENTAL_ADAPTER_NAMES",
    "FoliumAdapter",
    "GeospatialLayerAdapter",
    "GraphVizAdapter",
    "GreatTablesAdapter",
    "HoloViewsAdapter",
    "MapLibreAdapter",
    "MermaidAdapter",
    "PlotlyResamplingAdapter",
    "PyDeckAdapter",
    "PygalAdapter",
    "SigmaAdapter",
    "ThreeJsAdapter",
    "VegaLiteAdapter",
    "VegaTransformAdapter",
    "optional_adapters",
]

_logger = logging.getLogger("hedron.charts")


def _mapping(value: Any) -> Mapping[str, Any]:
    return cast(Mapping[str, Any], value)


def _json_output(
    *,
    kind: str,
    body: Mapping[str, Any] | Sequence[Any] | str,
    accessibility: ChartAccessibility,
    limits: VisualizationLimits | None,
    metadata: Mapping[str, Any] | None = None,
) -> ChartOutput:
    acc = accessibility.validated()
    payload = body if isinstance(body, str) else json.dumps(body, default=str)
    ensure_limits(None, payload, limits=limits)
    if isinstance(body, Mapping):
        reject_remote_urls(body)
        reject_callbacks(body)
    return ChartOutput(
        kind=kind,
        body=payload,
        accessibility=acc,
        media_type="application/json",
        payload_bytes=payload_size(payload),
        metadata=dict(metadata or {}),
    )


def _render_host(output: ChartOutput, host: str) -> NodeLike:
    return render_host_figure(output, host=host)


class VegaLiteAdapter:
    name = "vega-lite"
    optional_package = "altair"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and (
            str(mapping.get("$schema", "")).find("vega-lite") >= 0 or "mark" in mapping
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError("Vega-Lite adapter expects a mapping spec")
        return _json_output(
            kind="vega-lite",
            body=dict(_mapping(value)),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "vega-lite")


class VegaTransformAdapter:
    name = "vega-transform"
    optional_package = None

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and "transform" in value

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        mapping = _mapping(value)
        transforms_value: object = mapping.get("transform") or []
        if not isinstance(transforms_value, list):
            raise TypeError("transform must be a list")
        transforms: list[Any] = cast(list[Any], transforms_value)
        return _json_output(
            kind="vega-lite",
            body=dict(mapping),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name, "server_transforms": transforms},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "vega-lite")


class PyDeckAdapter:
    name = "pydeck"
    optional_package = "pydeck"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return "pydeck" in type(cast(object, value)).__module__ or (
            mapping is not None and "layers" in mapping
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping):
            raw_body: Mapping[str, Any] = dict(_mapping(value))
        else:
            try:
                importlib.import_module("pydeck")
            except ImportError as exc:
                raise missing_extra("pydeck") from exc
            to_json = getattr(value, "to_json", None)
            raw = to_json() if callable(to_json) else None
            if isinstance(raw, (str, bytes, bytearray)):
                parsed = json.loads(raw)
                if not isinstance(parsed, Mapping):
                    raise TypeError("PyDeck to_json() must return a mapping")
                raw_body = cast(Mapping[str, Any], parsed)
            else:
                raise TypeError(
                    "PyDeck value must expose to_json() returning MapLibre-compatible JSON"
                )
        body = extract_pydeck_payload(raw_body)
        return _json_output(
            kind="maplibre",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name, "source": "pydeck-extract"},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "maplibre")


class MapLibreAdapter:
    name = "maplibre"
    optional_package = None

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and ("style" in mapping or "maplibre" in mapping)

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        body = dict(_mapping(value))
        body.setdefault("coord_order", "lnglat")
        return _json_output(
            kind="maplibre",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "maplibre")


class FoliumAdapter:
    name = "folium"
    optional_package = "folium"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return "folium" in type(cast(object, value)).__module__ or (
            mapping is not None and mapping.get("type") == "folium"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            try:
                importlib.import_module("folium")
            except ImportError as exc:
                raise missing_extra("folium") from exc
        body = extract_folium_payload(cast(object, value))
        return _json_output(
            kind="maplibre",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name, "source": "folium-extract"},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "maplibre")


class GeospatialLayerAdapter:
    name = "geospatial"
    optional_package = None

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and mapping.get("type") in {
            "FeatureCollection",
            "Feature",
            "GeometryCollection",
        }

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        return _json_output(
            kind="maplibre",
            body={"geojson": dict(_mapping(value))},
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "maplibre")


class GraphVizAdapter:
    name = "graphviz"
    optional_package = "graphviz"

    def supports(self, value: object) -> bool:
        if "graphviz" in type(value).__module__:
            return True
        if not isinstance(value, str):
            return False
        stripped = value.lstrip()
        # Require DOT keyword at token start — avoid matching "graph" mid-sentence.
        return bool(re.match(r"(?:strict\s+)?(?:di)?graph\b", stripped, flags=re.IGNORECASE))

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        from hedron_core.diagnostics import HedronError

        source = value if isinstance(value, str) else str(getattr(value, "source", value))
        ensure_limits(None, source, limits=limits)
        svg: str | None = None
        try:
            graphviz = importlib.import_module("graphviz")
            src = graphviz.Source(source)
            rendered = src.pipe(format="svg")
            svg = rendered.decode("utf-8") if isinstance(rendered, bytes) else str(rendered)
            reject_active_svg(svg)
        except ImportError as exc:
            _logger.debug("graphviz not installed; falling back to DOT text: %s", exc)
            svg = None
        except HedronError:
            raise
        except Exception as exc:  # noqa: BLE001 — graphviz/subprocess surfaces vary
            _logger.warning("graphviz SVG render failed; falling back to DOT text: %s", exc)
            svg = None
        if svg is not None:
            return ChartOutput(
                kind="svg",
                body=svg,
                accessibility=accessibility.validated(),
                media_type="image/svg+xml",
                payload_bytes=payload_size(svg),
                metadata={"adapter": self.name, "format": "svg"},
            )
        return ChartOutput(
            kind="html",
            body=source,
            accessibility=accessibility.validated(),
            media_type="text/plain",
            payload_bytes=payload_size(source),
            metadata={"adapter": self.name, "format": "dot"},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        if output.media_type == "image/svg+xml" and isinstance(output.body, str):
            return html.figure(
                html.h2(acc.title),
                html.p(acc.description or ""),
                html.raw(TrustedHtml.reviewed(output.body, source="hedron-charts:graphviz")),
                class_="hedron-chart hedron-chart-graphviz",
            )
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.pre(str(output.body)),
            class_="hedron-chart hedron-chart-graphviz",
        )


class MermaidAdapter:
    name = "mermaid"
    optional_package = None

    def supports(self, value: object) -> bool:
        return isinstance(value, str) and value.strip().startswith(
            ("graph", "flowchart", "sequenceDiagram", "classDiagram")
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, str):
            raise TypeError(f"{self.name} adapter expected a string; got {type(value).__name__}")
        ensure_limits(None, value, limits=limits)
        return _json_output(
            kind="mermaid",
            body={"diagram": value},
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "mermaid")


class ChartJsAdapter:
    name = "chartjs"
    optional_package = None

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and mapping.get("type") in {
            "bar",
            "line",
            "pie",
            "doughnut",
            "radar",
            "scatter",
        }

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        return _json_output(
            kind="chartjs",
            body=dict(_mapping(value)),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "chartjs")


class GreatTablesAdapter:
    name = "great-tables"
    optional_package = "great_tables"

    def supports(self, value: object) -> bool:
        return "great_tables" in type(value).__module__

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            rows = [
                dict(_mapping(row))
                for row in cast(Sequence[object], value)
                if isinstance(row, Mapping)
            ]
            body = json.dumps(redact_rows(rows))
            ensure_limits(rows, body, limits=limits)
            return ChartOutput(
                kind="html",
                body=body,
                accessibility=accessibility.validated(),
                media_type="application/json",
                payload_bytes=payload_size(body),
                metadata={"adapter": self.name, "rows": len(rows)},
            )
        try:
            importlib.import_module("great_tables")
        except ImportError as exc:
            raise missing_extra("great_tables") from exc
        raw = str(value)
        reject_active_svg(raw)
        sanitized = TrustedHtml.nh3(raw)
        reject_active_svg(sanitized.value)
        return ChartOutput(
            kind="html",
            body=sanitized.value,
            accessibility=accessibility.validated(),
            media_type="text/html",
            payload_bytes=payload_size(sanitized.value),
            metadata={"adapter": self.name, "sanitizer": sanitized.source},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        body = output.body
        rows: list[dict[str, object]] = []
        if isinstance(body, str):
            try:
                parsed = json.loads(body)
                if isinstance(parsed, list):
                    rows = [
                        dict(_mapping(row))
                        for row in cast(list[object], parsed)
                        if isinstance(row, Mapping)
                    ]
            except json.JSONDecodeError:
                rows = []
        table_children: list[NodeLike] = []
        if rows:
            headers = list(rows[0].keys())
            head = html.tr(*[html.th(str(h)) for h in headers])
            body_rows = [html.tr(*[html.td(str(row.get(h, ""))) for h in headers]) for row in rows]
            table_children = [html.table(html.thead(head), html.tbody(*body_rows))]
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            *table_children,
            class_="hedron-chart hedron-chart-great-tables",
        )


class SigmaAdapter:
    name = "sigma"
    optional_package = "networkx"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return (
            mapping is not None
            and {"nodes", "edges"} <= set(mapping)
            or ("networkx" in type(cast(object, value)).__module__)
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping):
            body = dict(_mapping(value))
        else:
            try:
                nx = importlib.import_module("networkx")
            except ImportError as exc:
                raise missing_extra("networkx") from exc
            graph_type = getattr(nx, "Graph", object)
            if not isinstance(value, graph_type):
                raise TypeError("SigmaAdapter expects networkx.Graph or {nodes,edges}")
            nodes = getattr(value, "nodes", ())
            edges = getattr(value, "edges", ())
            body = {
                "nodes": [{"id": str(n)} for n in nodes],
                "edges": [{"source": str(u), "target": str(v)} for u, v in edges],
            }
        return _json_output(
            kind="html",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "sigma")


class ThreeJsAdapter:
    name = "threejs"
    optional_package = None
    _ALLOWED = frozenset({".gltf", ".glb", ".obj", ".stl", ".ply", ".fbx"})

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and "model_url" in mapping

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        mapping = _mapping(value)
        url = str(mapping.get("model_url") or "").strip()
        lower = url.lower()
        if not any(lower.endswith(ext) for ext in self._ALLOWED):
            raise ValueError(f"Model format not allowlisted: {url!r}")
        if url.startswith(("http://", "https://", "//", "data:", "file:", "javascript:")):
            reject_remote_urls({"url": url})
        # App-controlled local asset refs only; reject path traversal (#194, #262).
        decoded = unquote(url.replace("\\", "/"))
        parts = [p for p in decoded.split("/") if p not in ("", ".")]
        if ".." in parts:
            raise ValueError(f"Model path traversal rejected: {url!r}")
        from pathlib import Path

        measured: int | None = None
        local = Path(decoded)
        if local.is_file():
            measured = local.stat().st_size
        raw_bytes = mapping.get("bytes")
        claimed: int | None = None
        if raw_bytes is not None and str(raw_bytes).strip() != "":
            claimed = int(raw_bytes)
        size = measured if measured is not None else claimed
        if size is None or size <= 0:
            raise ValueError("Model size is required (bytes) or a readable local asset")
        lim = limits or VisualizationLimits()
        if size > lim.max_payload_bytes:
            raise ValueError("Model exceeds size budget")
        return _json_output(
            kind="html",
            body=dict(mapping),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "threejs")


class EChartsAdapter:
    name = "echarts"
    optional_package = None

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and ("series" in mapping or "xAxis" in mapping)

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        return _json_output(
            kind="html",
            body=dict(_mapping(value)),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "echarts")


class DatashaderAdapter:
    name = "datashader"
    optional_package = "datashader"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return "datashader" in type(cast(object, value)).__module__ or (
            mapping is not None and mapping.get("type") == "datashader"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        try:
            importlib.import_module("datashader")
        except ImportError as exc:
            raise missing_extra("datashader") from exc
        return _json_output(
            kind="png",
            body={"repr": str(value)},
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "static")


class BokehAdapter:
    name = "bokeh"
    optional_package = "bokeh"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return "bokeh" in type(cast(object, value)).__module__ or (
            mapping is not None and mapping.get("type") == "bokeh"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        try:
            importlib.import_module("bokeh")
        except ImportError as exc:
            if not isinstance(value, Mapping):
                raise missing_extra("bokeh") from exc
        body = dict(_mapping(value)) if isinstance(value, Mapping) else {"repr": str(value)}
        return _json_output(
            kind="html",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "bokeh")


class HoloViewsAdapter:
    name = "holoviews"
    optional_package = "holoviews"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return "holoviews" in type(cast(object, value)).__module__ or (
            mapping is not None and mapping.get("type") == "holoviews"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        try:
            importlib.import_module("holoviews")
        except ImportError as exc:
            if not isinstance(value, Mapping):
                raise missing_extra("holoviews") from exc
        body = dict(_mapping(value)) if isinstance(value, Mapping) else {"repr": str(value)}
        return _json_output(
            kind="html",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "holoviews")


class PygalAdapter:
    name = "pygal"
    optional_package = "pygal"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return "pygal" in type(cast(object, value)).__module__ or (
            mapping is not None and mapping.get("type") == "pygal"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping) and "svg" in value:
            svg = str(_mapping(value)["svg"])
        else:
            try:
                importlib.import_module("pygal")
            except ImportError as exc:
                raise missing_extra("pygal") from exc
            render = getattr(cast(object, value), "render", None)
            if callable(render):
                rendered = render()
                svg = rendered.decode("utf-8") if isinstance(rendered, bytes) else str(rendered)
            else:
                svg = str(cast(object, value))
        ensure_limits(None, svg, limits=limits)
        reject_active_svg(svg)
        return ChartOutput(
            kind="svg",
            body=svg,
            accessibility=accessibility.validated(),
            media_type="image/svg+xml",
            payload_bytes=payload_size(svg),
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        svg = output.body if isinstance(output.body, str) else ""
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.raw(TrustedHtml.reviewed(svg, source="hedron-charts:pygal")),
            class_="hedron-chart",
        )


class PlotlyResamplingAdapter:
    name = "plotly-resample"
    optional_package = "plotly"

    def supports(self, value: object) -> bool:
        mapping = _mapping(value) if isinstance(value, Mapping) else None
        return mapping is not None and mapping.get("resample") is not None

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if not isinstance(value, Mapping):
            raise TypeError(f"{self.name} adapter expected a mapping; got {type(value).__name__}")
        mapping = _mapping(value)
        raw_max = mapping.get("max_points", 1000)
        try:
            max_points = int(raw_max)  # type: ignore[arg-type]
        except (TypeError, ValueError) as exc:
            raise error(
                "HED-CHART-0002",
                title="Invalid chart max_points",
                explanation=f"max_points must be a positive integer; got {raw_max!r}.",
                remediation="Pass max_points >= 1 or omit it to use the default of 1000.",
            ) from exc
        if max_points < 1:
            raise error(
                "HED-CHART-0002",
                title="Invalid chart max_points",
                explanation=f"max_points must be a positive integer; got {max_points}.",
                remediation="Pass max_points >= 1 or omit it to use the default of 1000.",
            )
        body = downsample_plotly_body(dict(mapping), max_points=max_points)
        return _json_output(
            kind="plotly-json",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={
                "adapter": self.name,
                "max_points": max_points,
                "resampled": True,
            },
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_host(output, "plotly")


# Machine-readable Experimental inventory (INTERACTIVE-028 / D-056).
# Must stay aligned with docs/acceptance/production-grade-inventory-028.toml.
EXPERIMENTAL_ADAPTER_NAMES: frozenset[str] = frozenset(
    {
        "plotly",
        "altair",
        "vega_interactive_hosts",
        "vega-lite",
        "vega-transform",
        "pydeck",
        "maplibre",
        "folium",
        "geospatial",
        "graphviz",
        "mermaid",
        "chartjs",
        "great-tables",
        "sigma",
        "threejs",
        "echarts",
        "datashader",
        "bokeh",
        "holoviews",
        "pygal",
        "plotly-resample",
    }
)


def optional_adapters() -> list[object]:
    return [
        VegaLiteAdapter(),
        VegaTransformAdapter(),
        PyDeckAdapter(),
        MapLibreAdapter(),
        FoliumAdapter(),
        GeospatialLayerAdapter(),
        GraphVizAdapter(),
        MermaidAdapter(),
        ChartJsAdapter(),
        GreatTablesAdapter(),
        SigmaAdapter(),
        ThreeJsAdapter(),
        EChartsAdapter(),
        DatashaderAdapter(),
        BokehAdapter(),
        HoloViewsAdapter(),
        PygalAdapter(),
        PlotlyResamplingAdapter(),
    ]
