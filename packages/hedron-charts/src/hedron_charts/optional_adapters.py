"""Optional visualization adapters for phase 0.12 scale."""

from __future__ import annotations

import importlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

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
from hedron_core.html import html
from hedron_core.security import TrustedHtml
from hedron_core.visualization import ChartAccessibility, ChartOutput, VisualizationLimits

__all__ = [
    "BokehAdapter",
    "ChartJsAdapter",
    "DatashaderAdapter",
    "EChartsAdapter",
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


def _render_json(output: ChartOutput) -> NodeLike:
    acc = output.accessibility
    return html.figure(
        html.h2(acc.title),
        html.p(acc.description or acc.alt or ""),
        html.pre(str(output.body)[:2000]),
        class_=f"hedron-chart hedron-chart-{output.kind}",
        **{"role": "img", "aria-label": acc.alt or acc.title},
    )


class VegaLiteAdapter:
    name = "vega-lite"
    optional_package = "altair"

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and (
            value.get("$schema", "").find("vega-lite") >= 0 or "mark" in value
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
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


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
        assert isinstance(value, Mapping)
        transforms = value.get("transform") or []
        if not isinstance(transforms, list):
            raise TypeError("transform must be a list")
        return _json_output(
            kind="vega-lite",
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name, "server_transforms": transforms},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class PyDeckAdapter:
    name = "pydeck"
    optional_package = "pydeck"

    def supports(self, value: object) -> bool:
        return "pydeck" in type(value).__module__ or (
            isinstance(value, Mapping) and "layers" in value
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping):
            body = dict(value)
        else:
            try:
                importlib.import_module("pydeck")
            except ImportError as exc:
                raise missing_extra("pydeck") from exc
            to_json = getattr(value, "to_json", None)
            raw = to_json() if callable(to_json) else None
            if isinstance(raw, (str, bytes, bytearray)):
                body = json.loads(raw)
            else:
                body = {"repr": str(value)}
        return _json_output(
            kind="html",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class MapLibreAdapter:
    name = "maplibre"
    optional_package = None

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and ("style" in value or "maplibre" in value)

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        assert isinstance(value, Mapping)
        return _json_output(
            kind="html",
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class FoliumAdapter:
    name = "folium"
    optional_package = "folium"

    def supports(self, value: object) -> bool:
        return "folium" in type(value).__module__ or (
            isinstance(value, Mapping) and value.get("type") == "folium"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping):
            html_body = str(value.get("html") or "")
        else:
            try:
                importlib.import_module("folium")
            except ImportError as exc:
                raise missing_extra("folium") from exc
            repr_html = getattr(value, "_repr_html_", None)
            rendered = repr_html() if callable(repr_html) else str(value)
            html_body = rendered if isinstance(rendered, str) else str(rendered)
        ensure_limits(None, html_body, limits=limits)
        reject_active_svg(html_body)
        return ChartOutput(
            kind="html",
            body=html_body,
            accessibility=accessibility.validated(),
            media_type="text/html",
            payload_bytes=payload_size(html_body),
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        body = output.body if isinstance(output.body, str) else ""
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.raw(TrustedHtml.reviewed(body, source="hedron-charts:folium")),
            class_="hedron-chart hedron-chart-folium",
        )


class GeospatialLayerAdapter:
    name = "geospatial"
    optional_package = None

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and value.get("type") in {
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
        assert isinstance(value, Mapping)
        return _json_output(
            kind="html",
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class GraphVizAdapter:
    name = "graphviz"
    optional_package = "graphviz"

    def supports(self, value: object) -> bool:
        return (
            isinstance(value, str)
            and ("digraph" in value or "graph" in value)
            or ("graphviz" in type(value).__module__)
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        source = value if isinstance(value, str) else str(getattr(value, "source", value))
        ensure_limits(None, source, limits=limits)
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
        assert isinstance(value, str)
        ensure_limits(None, value, limits=limits)
        return ChartOutput(
            kind="html",
            body=value,
            accessibility=accessibility.validated(),
            media_type="text/plain",
            payload_bytes=payload_size(value),
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.pre(
                str(output.body),
                **{"data-hedron-mermaid": "1"},
            ),
            class_="hedron-chart hedron-chart-mermaid",
        )


class ChartJsAdapter:
    name = "chartjs"
    optional_package = None

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and value.get("type") in {
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
        assert isinstance(value, Mapping)
        return _json_output(
            kind="html",
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class GreatTablesAdapter:
    name = "great-tables"
    optional_package = "great_tables"

    def supports(self, value: object) -> bool:
        return "great_tables" in type(value).__module__ or isinstance(value, (list, tuple))

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            rows = [dict(row) for row in value if isinstance(row, Mapping)]
            ensure_limits(rows, None, limits=limits)
            return ChartOutput(
                kind="html",
                body=json.dumps(redact_rows(rows)),
                accessibility=accessibility.validated(),
                media_type="application/json",
                payload_bytes=payload_size(json.dumps(rows)),
                metadata={"adapter": self.name, "rows": len(rows)},
            )
        try:
            importlib.import_module("great_tables")
        except ImportError as exc:
            raise missing_extra("great_tables") from exc
        return ChartOutput(
            kind="html",
            body=str(value),
            accessibility=accessibility.validated(),
            media_type="text/html",
            payload_bytes=payload_size(str(value)),
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        return html.figure(html.h2(acc.title), html.p(acc.description or ""), class_="hedron-chart")


class SigmaAdapter:
    name = "sigma"
    optional_package = "networkx"

    def supports(self, value: object) -> bool:
        return (
            isinstance(value, Mapping)
            and {"nodes", "edges"} <= set(value)
            or ("networkx" in type(value).__module__)
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping):
            body = dict(value)
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
        return _render_json(output)


class ThreeJsAdapter:
    name = "threejs"
    optional_package = None
    _ALLOWED = frozenset({".gltf", ".glb", ".obj", ".stl", ".ply", ".fbx"})

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and "model_url" in value

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        assert isinstance(value, Mapping)
        url = str(value.get("model_url") or "")
        lower = url.lower()
        if not any(lower.endswith(ext) for ext in self._ALLOWED):
            raise ValueError(f"Model format not allowlisted: {url!r}")
        if url.startswith(("http://", "https://", "//")):
            reject_remote_urls({"url": url})
        size = int(value.get("bytes") or 0)
        lim = limits or VisualizationLimits()
        if size > lim.max_payload_bytes:
            raise ValueError("Model exceeds size budget")
        return _json_output(
            kind="html",
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class EChartsAdapter:
    name = "echarts"
    optional_package = None

    def supports(self, value: object) -> bool:
        return isinstance(value, Mapping) and ("series" in value or "xAxis" in value)

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        assert isinstance(value, Mapping)
        return _json_output(
            kind="html",
            body=dict(value),
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class DatashaderAdapter:
    name = "datashader"
    optional_package = "datashader"

    def supports(self, value: object) -> bool:
        return "datashader" in type(value).__module__ or (
            isinstance(value, Mapping) and value.get("type") == "datashader"
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
        return _render_json(output)


class BokehAdapter:
    name = "bokeh"
    optional_package = "bokeh"

    def supports(self, value: object) -> bool:
        return "bokeh" in type(value).__module__ or (
            isinstance(value, Mapping) and value.get("type") == "bokeh"
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
        body = dict(value) if isinstance(value, Mapping) else {"repr": str(value)}
        return _json_output(
            kind="html",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class HoloViewsAdapter:
    name = "holoviews"
    optional_package = "holoviews"

    def supports(self, value: object) -> bool:
        return "holoviews" in type(value).__module__ or (
            isinstance(value, Mapping) and value.get("type") == "holoviews"
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
        body = dict(value) if isinstance(value, Mapping) else {"repr": str(value)}
        return _json_output(
            kind="html",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


class PygalAdapter:
    name = "pygal"
    optional_package = "pygal"

    def supports(self, value: object) -> bool:
        return "pygal" in type(value).__module__ or (
            isinstance(value, Mapping) and value.get("type") == "pygal"
        )

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        if isinstance(value, Mapping) and "svg" in value:
            svg = str(value["svg"])
        else:
            try:
                importlib.import_module("pygal")
            except ImportError as exc:
                raise missing_extra("pygal") from exc
            render = getattr(value, "render", None)
            if callable(render):
                rendered = render()
                svg = rendered.decode("utf-8") if isinstance(rendered, bytes) else str(rendered)
            else:
                svg = str(value)
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
        return isinstance(value, Mapping) and value.get("resample") is not None

    def compile(
        self,
        value: object,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        assert isinstance(value, Mapping)
        body = dict(value)
        max_points = int(body.get("max_points") or 1000)
        return _json_output(
            kind="plotly-json",
            body=body,
            accessibility=accessibility,
            limits=limits,
            metadata={"adapter": self.name, "max_points": max_points},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        return _render_json(output)


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
