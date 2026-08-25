"""Matplotlib, Plotly, and Altair visualization adapters."""

from __future__ import annotations

import base64
import io
import json
import math
from collections.abc import Mapping, Sequence

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
from hedron_core.typing_aliases import JsonValue
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


def _json_safe(value: object) -> object:
    """Normalize array/scalar adapters and non-finite numbers to JSON values."""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        try:
            return _json_safe(tolist())
        except (TypeError, ValueError):
            pass
    item = getattr(value, "item", None)
    if callable(item):
        try:
            return _json_safe(item())
        except (TypeError, ValueError):
            pass
    return value


def _strict_payload(value: object) -> str:
    return json.dumps(_json_safe(value), separators=(",", ":"), allow_nan=False, default=str)


class MatplotlibAdapter:
    name = "matplotlib"
    optional_package = "matplotlib"

    def supports(self, value: object) -> bool:
        mod = type(value).__module__
        name = type(value).__name__
        return "matplotlib" in mod and ("Figure" in name or hasattr(value, "savefig"))

    def compile(
        self,
        value: object,
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
        savefig = getattr(value, "savefig", None)
        if not callable(savefig):
            raise TypeError("matplotlib adapter requires a Figure-like object with savefig()")
        if fmt == "png":
            savefig(buf, format="png", bbox_inches="tight")
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
        savefig(buf, format="svg", bbox_inches="tight")
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
        from hedron_core.diagnostics import error

        acc = output.accessibility
        children: list[NodeLike] = [html.h2(acc.title)]
        if acc.description:
            children.append(html.p(acc.description))
        if output.kind == "svg":
            svg = str(output.body)
            reject_active_svg(svg)
            children.append(html.raw(TrustedHtml.reviewed(svg, source="matplotlib:svg")))
        else:
            import html as html_stdlib
            import re

            encoded = str(output.body).strip()
            if not re.fullmatch(r"[A-Za-z0-9+/]+=*", encoded):
                raise error(
                    "HED-CHART-0007",
                    title="Invalid chart PNG payload",
                    explanation="PNG chart body must be strict base64.",
                    remediation="Compile charts through MatplotlibAdapter.compile().",
                )
            try:
                base64.b64decode(encoded, validate=True)
            except Exception as exc:
                raise error(
                    "HED-CHART-0007",
                    title="Invalid chart PNG payload",
                    explanation="PNG chart body must be strict base64.",
                    remediation="Compile charts through MatplotlibAdapter.compile().",
                ) from exc
            # Alphabet-validated body cannot break out of the quoted attribute.
            alt = html_stdlib.escape(acc.alt or acc.title, quote=True)
            img_html = f'<img src="data:image/png;base64,{encoded}" alt="{alt}" />'
            children.append(html.raw(TrustedHtml.reviewed(img_html, source="matplotlib:png")))
        if acc.tabular_fallback:
            children.append(_fallback_table(acc.tabular_fallback))
        return html.figure(*children, class_="hedron-chart hedron-chart-matplotlib")


class PlotlyAdapter:
    name = "plotly"
    optional_package = "plotly"

    def supports(self, value: object) -> bool:
        return type(value).__module__.startswith("plotly")

    def compile(
        self,
        value: object,
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
        to_json = getattr(value, "to_plotly_json", None)
        fig_dict = to_json() if callable(to_json) else value
        reject_callbacks(fig_dict)
        reject_remote_urls(fig_dict)
        try:
            from plotly.utils import PlotlyJSONEncoder  # type: ignore[reportMissingImports]

            body = json.dumps(
                fig_dict,
                separators=(",", ":"),
                allow_nan=False,
                cls=PlotlyJSONEncoder,
            )
        except (ImportError, TypeError, ValueError):
            body = _strict_payload(fig_dict)
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

    def supports(self, value: object) -> bool:
        mod = type(value).__module__
        return mod.startswith("altair") or "vega" in mod.lower()

    def compile(
        self,
        value: object,
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
        to_dict = getattr(value, "to_dict", None)
        if callable(to_dict):
            raw_spec = to_dict()
            if not isinstance(raw_spec, dict):
                raise TypeError("Altair adapter expects to_dict() to return a mapping")
            spec: dict[str, object] = dict(raw_spec)
        elif isinstance(value, dict):
            spec = {str(k): v for k, v in value.items()}
        else:
            raise TypeError("Altair adapter expects a Chart or Vega-Lite dict")
        # Altair emits a remote JSON-schema identifier as metadata. The browser
        # renderer does not fetch it, and removing it keeps otherwise local chart
        # payloads compatible with Hedron's remote-resource policy.
        spec.pop("$schema", None)
        reject_callbacks(spec)
        reject_remote_urls(spec)
        body = _strict_payload(spec)
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


def _fallback_table(
    rows: Sequence[Mapping[str, JsonValue]] | None,
    *,
    max_rows: int | None = None,
) -> NodeLike:
    """Bounded tabular fallback that retains every admitted row (#82).

    Cap is ``VisualizationLimits.max_rows`` (or an explicit ``max_rows``), never a
    silent hard-coded slice that drops admitted data.
    """
    from hedron_core.visualization import DEFAULT_MAX_CHART_ROWS

    cleaned = redact_rows(list(rows or ()))
    if not cleaned:
        return Text("")
    limit = DEFAULT_MAX_CHART_ROWS if max_rows is None else max(0, int(max_rows))
    admitted = cleaned[:limit]
    headers = list(admitted[0].keys())
    head = html.tr(*[html.th(h) for h in headers])
    body = [html.tr(*[html.td(str(row.get(h, ""))) for h in headers]) for row in admitted]
    return html.table(html.thead(head), html.tbody(*body), class_="hedron-chart-fallback")


_ADAPTERS = (MatplotlibAdapter(), PlotlyAdapter(), AltairAdapter())


def adapter_for(value: object) -> MatplotlibAdapter | PlotlyAdapter | AltairAdapter:
    for adapter in _ADAPTERS:
        if adapter.supports(value):
            return adapter
    raise missing_extra("all")


def compile_figure(
    value: object,
    *,
    title: str,
    description: str | None = None,
    alt: str | None = None,
    waiver: str | None = None,
    tabular_fallback: Sequence[Mapping[str, JsonValue]] | None = None,
    limits: VisualizationLimits | None = None,
) -> tuple[MatplotlibAdapter | PlotlyAdapter | AltairAdapter, ChartOutput]:
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
