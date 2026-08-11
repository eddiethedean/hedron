"""Register hedron-charts components, assets, Auto renderers, and Explorer panel."""

from __future__ import annotations

from pathlib import Path

from hedron_charts.adapters import AltairAdapter, MatplotlibAdapter, PlotlyAdapter
from hedron_charts.components import (
    AltairChart,
    AreaChart,
    BarChart,
    LineChart,
    MatplotlibChart,
    PlotlyChart,
    ScatterChart,
)
from hedron_charts.pins import assert_pins_present
from hedron_core.auto import RendererSpec, register_renderer
from hedron_core.component import NodeLike
from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset, register_browser_module, register_component

_ROOT = Path(__file__).resolve().parent
_PLOTLY_HOST = _ROOT / "assets" / "plotly" / "host.js"
_VEGA_HOST = _ROOT / "assets" / "vega" / "host.js"
_OPTIONAL_HOSTS = (
    (_ROOT / "assets" / "chartjs" / "host.js", "hedron-charts:chartjs.host.js", "chartjs"),
    (_ROOT / "assets" / "echarts" / "host.js", "hedron-charts:echarts.host.js", "echarts"),
    (_ROOT / "assets" / "mermaid" / "host.js", "hedron-charts:mermaid.host.js", "mermaid"),
    (_ROOT / "assets" / "maplibre" / "host.js", "hedron-charts:maplibre.host.js", "maplibre"),
    (_ROOT / "assets" / "static" / "host.js", "hedron-charts:static.host.js", "static"),
)
_OPTIONAL_RUNTIMES = (
    (_ROOT / "assets" / "plotly" / "plotly.min.js", "hedron-charts:plotly.runtime.js"),
    (_ROOT / "assets" / "vega" / "vega.min.js", "hedron-charts:vega.runtime.js"),
    (_ROOT / "assets" / "vega" / "vega-embed.min.js", "hedron-charts:vega-embed.runtime.js"),
    (_ROOT / "assets" / "chartjs" / "chart.umd.min.js", "hedron-charts:chartjs.runtime.js"),
    (_ROOT / "assets" / "echarts" / "echarts.min.js", "hedron-charts:echarts.runtime.js"),
    (_ROOT / "assets" / "mermaid" / "mermaid.min.js", "hedron-charts:mermaid.runtime.js"),
    (_ROOT / "assets" / "maplibre" / "maplibre-gl.js", "hedron-charts:maplibre.runtime.js"),
)

PLUGIN_META = PluginMeta(
    name="hedron_charts",
    version="0.1.11",
    distribution="hedron-charts",
    hedron_version=">=0.28,<0.29",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)


def _factory_matplotlib(value: object) -> NodeLike:
    return MatplotlibChart(value, title="Chart", description="Auto-rendered Matplotlib figure")


def _factory_plotly(value: object) -> NodeLike:
    return PlotlyChart(value, description="Auto-rendered Plotly figure")


def _factory_altair(value: object) -> NodeLike:
    return AltairChart(value, description="Auto-rendered Altair chart")


def register(ctx: PluginContext) -> None:
    assert_pins_present()
    for cls in (
        LineChart,
        AreaChart,
        BarChart,
        ScatterChart,
        MatplotlibChart,
        PlotlyChart,
        AltairChart,
    ):
        logical = f"{cls.distribution}:{cls.__module__}.{cls.logical_name}"
        register_component(
            logical_id=logical,
            name=cls.logical_name or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=cls.props_type.__name__,
            accessibility_notes=(
                "Charts require title and description/alt/waiver; tabular fallbacks when provided."
            ),
        )

    for path, logical_id, kind in (
        (_PLOTLY_HOST, "hedron-charts:plotly.host.js", "js"),
        (_VEGA_HOST, "hedron-charts:vega.host.js", "js"),
    ):
        if path.is_file():
            digest = content_digest(path.read_bytes())
            register_asset(
                logical_id=logical_id,
                kind=kind,
                path=str(path),
                digest=digest,
                content_type="text/javascript",
            )
    for path, logical_id, _host in _OPTIONAL_HOSTS:
        if path.is_file():
            register_asset(
                logical_id=logical_id,
                kind="js",
                path=str(path),
                digest=content_digest(path.read_bytes()),
                content_type="text/javascript",
            )
    for path, logical_id in _OPTIONAL_RUNTIMES:
        if path.is_file():
            register_asset(
                logical_id=logical_id,
                kind="js",
                path=str(path),
                digest=content_digest(path.read_bytes()),
                content_type="text/javascript",
            )

    _CHART_EVENTS = (
        "hedron-chart-hover",
        "hedron-chart-click",
        "hedron-chart-select",
        "hedron-chart-relayout",
        "hedron-chart-restyle",
    )
    if _PLOTLY_HOST.is_file():
        register_browser_module(
            logical_id="hedron-charts:plotly-host",
            tag_name="hedron-plotly-chart",
            module_path=str(_PLOTLY_HOST),
            observed_attributes=("data-hedron-payload",),
            events=_CHART_EVENTS,
            shadow_dom=False,
            htmx_lifecycle=True,
        )
    if _VEGA_HOST.is_file():
        register_browser_module(
            logical_id="hedron-charts:vega-host",
            tag_name="hedron-vega-chart",
            module_path=str(_VEGA_HOST),
            observed_attributes=("data-hedron-payload",),
            events=_CHART_EVENTS,
            shadow_dom=False,
            htmx_lifecycle=True,
        )

    # Matplotlib is the Supported production Auto default (INTERACTIVE-028).
    # Plotly/Altair remain registered for explicit as_= opt-in only.
    # Replace core chart-stub so fail-closed copy mentions Experimental opt-in
    # instead of "Install hedron-charts" when this package is already loaded.
    def _factory_chart_opt_in(value: object) -> NodeLike:
        from hedron_core.diagnostics import error

        raise error(
            "HED-AUTO-0004",
            title="Experimental chart backend requires explicit as_",
            explanation=(
                f"No Supported Auto renderer matched "
                f"{type(value).__module__}.{type(value).__name__}. "
                "Plotly and Altair are Experimental and are excluded from "
                "production Auto defaults."
            ),
            remediation=(
                "Use as_='plotly' or as_='altair' for Experimental backends, "
                "or pass a Matplotlib Figure for the Supported Auto chart path."
            ),
        )

    register_renderer(
        RendererSpec(
            name="matplotlib",
            priority=910,
            predicate=MatplotlibAdapter().supports,
            optional_package="hedron-charts[matplotlib]",
            explanation="Matplotlib Figure → MatplotlibChart",
            factory=_factory_matplotlib,
            maturity="supported",
        )
    )
    register_renderer(
        RendererSpec(
            name="plotly",
            priority=920,
            predicate=PlotlyAdapter().supports,
            optional_package="hedron-charts[plotly]",
            explanation="Plotly figure → PlotlyChart (Experimental; opt-in via as_)",
            factory=_factory_plotly,
            maturity="experimental",
        )
    )
    register_renderer(
        RendererSpec(
            name="altair",
            priority=915,
            predicate=AltairAdapter().supports,
            optional_package="hedron-charts[altair]",
            explanation="Altair/Vega-Lite → AltairChart (Experimental; opt-in via as_)",
            factory=_factory_altair,
            maturity="experimental",
        )
    )
    register_renderer(
        RendererSpec(
            name="chart-stub",
            priority=900,
            predicate=lambda v: (
                PlotlyAdapter().supports(v)
                or AltairAdapter().supports(v)
                or MatplotlibAdapter().supports(v)
            ),
            optional_package="hedron-charts",
            explanation="Fail closed when Supported Auto chart path does not match",
            factory=_factory_chart_opt_in,
            maturity="supported",
        )
    )

    ctx.register_explorer_panel(
        panel_id="hedron-charts-viz",
        title="Visualization",
        description="Chart backend, payload, assets, accessibility, and security policy",
        path="/hedron-explorer/charts",
    )
    ctx.register_diagnostic_owner("HED-CHART-")


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
