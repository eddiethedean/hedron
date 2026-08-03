"""Matplotlib, Plotly, and Altair visualization adapters."""

from __future__ import annotations

import base64
import io
import json
from typing import Any

from hedron_charts.limits import (
    accessibility_or_raise,
    ensure_limits,
    missing_extra,
    payload_size,
    redact_rows,
    reject_active_svg,
    reject_callbacks,
    reject_remote_urls,
)
from hedron_core.builtins.content import Text
from hedron_core.builtins.utilities import JSONViewer
from hedron_core.component import NodeLike
from hedron_core.html import html
from hedron_core.security import TrustedHtml
from hedron_core.visualization import (
    ChartAccessibility,
    ChartOutput,
    VisualizationLimits,
)

__all__ = [
    "AltairAdapter",
    "MatplotlibAdapter",
    "PlotlyAdapter",
    "adapter_for",
    "compile_figure",
]


class MatplotlibAdapter:
    name = "matplotlib"
    optional_package = "matplotlib"

    def supports(self, value: Any) -> bool:
        mod = type(value).__module__
        name = type(value).__name__
        return "matplotlib" in mod and ("Figure" in name or hasattr(value, "savefig"))

    def compile(
        self,
        value: Any,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
        fmt: str = "svg",
    ) -> ChartOutput:
        try:
            import importlib

            importlib.import_module("matplotlib")
        except ImportError as exc:
            raise missing_extra("matplotlib") from exc
        acc = accessibility.validated()
        buf = io.BytesIO()
        if fmt == "png":
            value.savefig(buf, format="png", bbox_inches="tight")
            raw = buf.getvalue()
            ensure_limits(None, raw, limits=limits)
            encoded = base64.b64encode(raw).decode("ascii")
            return ChartOutput(
                kind="png",
                body=encoded,
                accessibility=acc,
                media_type="image/png",
                payload_bytes=len(raw),
                metadata={"format": "png"},
            )
        value.savefig(buf, format="svg", bbox_inches="tight")
        svg = buf.getvalue().decode("utf-8")
        ensure_limits(None, svg, limits=limits)
        reject_active_svg(svg)
        return ChartOutput(
            kind="svg",
            body=svg,
            accessibility=acc,
            media_type="image/svg+xml",
            payload_bytes=payload_size(svg),
            metadata={"format": "svg"},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        children: list[Any] = [html.h2(acc.title)]
        if acc.description:
            children.append(html.p(acc.description))
        if output.kind == "svg":
            children.append(
                html.raw(TrustedHtml.reviewed(str(output.body), source="matplotlib:svg"))
            )
        else:
            alt = acc.alt or acc.title
            img_html = (
                f'<img src="data:image/png;base64,{output.body}" '
                f'alt="{alt.replace(chr(34), "")}" />'
            )
            children.append(html.raw(TrustedHtml.reviewed(img_html, source="matplotlib:png")))
        if acc.tabular_fallback:
            children.append(_fallback_table(acc.tabular_fallback))
        return html.figure(*children, class_="hedron-chart hedron-chart-matplotlib")


class PlotlyAdapter:
    name = "plotly"
    optional_package = "plotly"

    def supports(self, value: Any) -> bool:
        return type(value).__module__.startswith("plotly")

    def compile(
        self,
        value: Any,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        try:
            import importlib

            importlib.import_module("plotly.io")
        except ImportError as exc:
            raise missing_extra("plotly") from exc
        acc = accessibility.validated()
        fig_dict = value.to_plotly_json() if hasattr(value, "to_plotly_json") else value
        reject_callbacks(fig_dict)
        reject_remote_urls(fig_dict)
        body = json.dumps(fig_dict, separators=(",", ":"), default=str)
        ensure_limits(None, body, limits=limits)
        return ChartOutput(
            kind="plotly-json",
            body=body,
            accessibility=acc,
            media_type="application/json",
            assets=("hedron-charts:plotly.host.js",),
            payload_bytes=payload_size(body),
            metadata={"backend": "plotly"},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        payload = {
            "spec": json.loads(str(output.body)),
            "title": acc.title,
            "description": acc.description,
        }
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.div(
                data={
                    "hedron-chart": "plotly",
                    "hedron-payload": json.dumps(payload, separators=(",", ":")),
                },
                role="img",
                aria={"label": acc.alt or acc.title},
            ),
            _fallback_table(acc.tabular_fallback) if acc.tabular_fallback else Text(""),
            class_="hedron-chart hedron-chart-plotly",
        )


class AltairAdapter:
    name = "altair"
    optional_package = "altair"

    def supports(self, value: Any) -> bool:
        mod = type(value).__module__
        return mod.startswith("altair") or "vega" in mod.lower()

    def compile(
        self,
        value: Any,
        *,
        accessibility: ChartAccessibility,
        limits: VisualizationLimits | None = None,
    ) -> ChartOutput:
        try:
            import importlib

            importlib.import_module("altair")
        except ImportError as exc:
            raise missing_extra("altair") from exc
        acc = accessibility.validated()
        if hasattr(value, "to_dict"):
            spec = value.to_dict()
        elif isinstance(value, dict):
            spec = value
        else:
            raise TypeError("Altair adapter expects a Chart or Vega-Lite dict")
        reject_callbacks(spec)
        reject_remote_urls(spec)
        body = json.dumps(spec, separators=(",", ":"), default=str)
        ensure_limits(None, body, limits=limits)
        return ChartOutput(
            kind="vega-lite",
            body=body,
            accessibility=acc,
            media_type="application/json",
            assets=("hedron-charts:vega.host.js",),
            payload_bytes=payload_size(body),
            metadata={"backend": "altair"},
        )

    def render_node(self, output: ChartOutput) -> NodeLike:
        acc = output.accessibility
        payload = {
            "spec": json.loads(str(output.body)),
            "title": acc.title,
            "description": acc.description,
        }
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.div(
                data={
                    "hedron-chart": "vega-lite",
                    "hedron-payload": json.dumps(payload, separators=(",", ":")),
                },
                role="img",
                aria={"label": acc.alt or acc.title},
            ),
            _fallback_table(acc.tabular_fallback) if acc.tabular_fallback else Text(""),
            class_="hedron-chart hedron-chart-altair",
        )


def _fallback_table(rows: Any) -> NodeLike:
    cleaned = redact_rows(list(rows))
    if not cleaned:
        return Text("")
    headers = list(cleaned[0].keys())
    head = html.tr(*[html.th(h) for h in headers])
    body = [html.tr(*[html.td(str(row.get(h, ""))) for h in headers]) for row in cleaned[:50]]
    return html.table(html.thead(head), html.tbody(*body), class_="hedron-chart-fallback")


_ADAPTERS = (MatplotlibAdapter(), PlotlyAdapter(), AltairAdapter())


def adapter_for(value: Any) -> MatplotlibAdapter | PlotlyAdapter | AltairAdapter:
    for adapter in _ADAPTERS:
        if adapter.supports(value):
            return adapter
    raise missing_extra("all")


def compile_figure(
    value: Any,
    *,
    title: str,
    description: str | None = None,
    alt: str | None = None,
    waiver: str | None = None,
    tabular_fallback: Any = None,
    limits: VisualizationLimits | None = None,
) -> tuple[Any, ChartOutput]:
    acc = accessibility_or_raise(
        title=title,
        description=description,
        alt=alt,
        waiver=waiver,
        tabular_fallback=tabular_fallback,
    )
    adapter = adapter_for(value)
    return adapter, adapter.compile(value, accessibility=acc, limits=limits)


# Silence unused import warning for JSONViewer re-export convenience in Explorer
_ = JSONViewer
