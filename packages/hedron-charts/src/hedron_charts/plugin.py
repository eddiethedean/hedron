"""Register hedron-charts components, assets, Auto renderers, and Explorer panel."""

from __future__ import annotations

from pathlib import Path

from hedron_charts.adapters import AltairAdapter, MatplotlibAdapter, PlotlyAdapter
from hedron_charts.components import (
    AltairChart,
    AreaChart,
    BarChart,
    Chart,
    LineChart,
    MatplotlibChart,
    PlotlyChart,
    ScatterChart,
)
from hedron_charts.pins import assert_pins_present
from hedron_core.auto import RendererSpec
from hedron_core.component import NodeLike
from hedron_core.identifiers import content_digest
from hedron_core.plugins import (
    PluginCapabilities,
    PluginContext,
    PluginDefinition,
    PluginMeta,
)
from hedron_core.registry import ElementFieldOwnership

_ROOT = Path(__file__).resolve().parent
_PLOTLY_HOST = _ROOT / "assets" / "plotly" / "host.js"
_VEGA_HOST = _ROOT / "assets" / "vega" / "host.js"
_CHART_MODULE = _ROOT / "static" / "hedron-chart.mjs"
_CHART_CSS = _ROOT / "static" / "hedron-chart.css"
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
    version="0.2.4",
    distribution="hedron-charts",
    hedron_version=">=1.0,<2.0",
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


def _register_components(ctx: PluginContext) -> None:
    assert_pins_present()
    for cls in (
        LineChart,
        AreaChart,
        BarChart,
        ScatterChart,
        MatplotlibChart,
        PlotlyChart,
        AltairChart,
        Chart,
    ):
        logical = f"{cls.distribution}:{cls.__module__}.{cls.logical_name}"
        ctx.register_component(
            logical_id=logical,
            name=cls.logical_name or cls.__name__,
            module=cls.__module__,
            distribution=cls.distribution,
            props_model=cls.props_type.__name__,
            accessibility_notes=(
                "Charts require title and description/alt/waiver; tabular fallbacks when provided."
            ),
        )


def _register_primary_element(ctx: PluginContext) -> None:
    if _CHART_MODULE.is_file():
        ctx.register_asset(
            logical_id="hedron-charts:hedron-chart.mjs",
            kind="js",
            path=str(_CHART_MODULE),
            digest=content_digest(_CHART_MODULE.read_bytes()),
            content_type="text/javascript",
        )
        ctx.register_browser_module(
            logical_id="hedron-charts:hedron-chart",
            tag_name="hedron-chart",
            module_path=str(_CHART_MODULE),
            observed_attributes=("data-hedron-payload", "data-hedron-abi"),
            events=(
                "hedron-chart-inspect",
                "hedron-chart-focus",
                "hedron-chart-select",
                "hedron-chart-legend_filter",
                "hedron-chart-brush",
                "hedron-chart-zoom",
                "hedron-chart-pan",
                "hedron-chart-reset",
                "hedron-chart-crosshair",
                "hedron-chart-drill_intent",
            ),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
        ctx.register_element_definition(
            logical_id="hedron-chart",
            tag_name="hedron-chart",
            abi_version=1,
            module_asset_id="hedron-charts:hedron-chart.mjs",
            attributes=("data-hedron-payload", "data-hedron-abi", "data-hedron-element"),
            state_ownership=(
                ElementFieldOwnership(
                    name="payload",
                    mode="controlled",
                    reflection="attribute",
                    incoming_update="replace",
                    persistence="none",
                    event="hedron-chart-select",
                ),
            ),
            events=(
                "hedron-chart-inspect",
                "hedron-chart-focus",
                "hedron-chart-select",
                "hedron-chart-legend_filter",
                "hedron-chart-brush",
                "hedron-chart-zoom",
                "hedron-chart-pan",
                "hedron-chart-reset",
                "hedron-chart-crosshair",
                "hedron-chart-drill_intent",
            ),
            dom_policy="light",
            server_regions=("content",),
            a11y_contract={
                "role": "group",
                "name_from": "aria-label",
                "keyboard": "focusable-marks",
            },
            style_contract={"tokens": "--hedron-chart-*"},
            resources=("hedron-charts:hedron-chart.mjs", "hedron-charts:hedron-chart.css"),
            lifecycle={
                "connect": "idempotent",
                "disconnect": "abort+dispose",
                "htmx": "beforeCleanupElement",
            },
            fallback={
                "figure": "semantic",
                "summary": "compiled",
                "table": "bounded",
            },
            first_party=True,
        )
    if _CHART_CSS.is_file():
        ctx.register_asset(
            logical_id="hedron-charts:hedron-chart.css",
            kind="css",
            path=str(_CHART_CSS),
            digest=content_digest(_CHART_CSS.read_bytes()),
            content_type="text/css",
        )


def _register_runtime_assets(ctx: PluginContext) -> None:
    for path, logical_id, kind in (
        (_PLOTLY_HOST, "hedron-charts:plotly.host.js", "js"),
        (_VEGA_HOST, "hedron-charts:vega.host.js", "js"),
    ):
        if path.is_file():
            digest = content_digest(path.read_bytes())
            ctx.register_asset(
                logical_id=logical_id,
                kind=kind,
                path=str(path),
                digest=digest,
                content_type="text/javascript",
            )
    for path, logical_id, _host in _OPTIONAL_HOSTS:
        if path.is_file():
            ctx.register_asset(
                logical_id=logical_id,
                kind="js",
                path=str(path),
                digest=content_digest(path.read_bytes()),
                content_type="text/javascript",
            )
    for path, logical_id in _OPTIONAL_RUNTIMES:
        if path.is_file():
            ctx.register_asset(
                logical_id=logical_id,
                kind="js",
                path=str(path),
                digest=content_digest(path.read_bytes()),
                content_type="text/javascript",
            )


def _register_vendor_hosts(ctx: PluginContext) -> None:
    chart_events = (
        "hedron-chart-hover",
        "hedron-chart-click",
        "hedron-chart-select",
        "hedron-chart-relayout",
        "hedron-chart-restyle",
    )
    if _PLOTLY_HOST.is_file():
        ctx.register_browser_module(
            logical_id="hedron-charts:plotly-host",
            tag_name="hedron-plotly-chart",
            module_path=str(_PLOTLY_HOST),
            observed_attributes=("data-hedron-payload",),
            events=chart_events,
            shadow_dom=False,
            htmx_lifecycle=True,
        )
    if _VEGA_HOST.is_file():
        ctx.register_browser_module(
            logical_id="hedron-charts:vega-host",
            tag_name="hedron-vega-chart",
            module_path=str(_VEGA_HOST),
            observed_attributes=("data-hedron-payload",),
            events=chart_events,
            shadow_dom=False,
            htmx_lifecycle=True,
        )


def _register_renderers(ctx: PluginContext) -> None:
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

    ctx.register_renderer(
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
    ctx.register_renderer(
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
    ctx.register_renderer(
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
    ctx.register_renderer(
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


def _register_catalog(ctx: PluginContext) -> None:
    ctx.register_explorer_provider(
        panel_id="hedron-charts-viz",
        title="Visualization",
        description="Chart backend, payload, assets, accessibility, and security policy",
        path="/hedron-explorer/charts",
        capabilities=("html",),
    )
    ctx.register_diagnostic_owner("HED-CHART-")
    from hedron_core.catalog import SurfaceProjectionProvider

    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.charts",
            provider="hedron-charts",
            provider_version=PLUGIN_META.version,
            surface="Chart/LineChart/BarChart",
            limitations=("current surface plus opt-in ChartInteraction via include_feature",),
        )
    )
    ctx.register_projection_provider(
        SurfaceProjectionProvider(
            namespace="hedron.charts.interaction",
            provider="hedron-charts",
            provider_version=PLUGIN_META.version,
            surface="ChartInteraction",
            limitations=("Supported events: select, inspect, focus, reset",),
        )
    )


PLUGIN = PluginDefinition.from_callbacks(
    PLUGIN_META,
    (
        ("components", _register_components),
        ("primary-element", _register_primary_element),
        ("runtime-assets", _register_runtime_assets),
        ("vendor-hosts", _register_vendor_hosts),
        ("renderers", _register_renderers),
        ("catalog", _register_catalog),
    ),
)


def register(ctx: PluginContext) -> None:
    PLUGIN.register(ctx)


register.PLUGIN_META = PLUGIN_META  # type: ignore[attr-defined]
