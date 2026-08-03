"""Register hedron-charts components, assets, Auto renderers, and Explorer panel."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hedron_charts.adapters import AltairAdapter, MatplotlibAdapter, PlotlyAdapter
from hedron_charts.components import AltairChart, LineChart, MatplotlibChart, PlotlyChart
from hedron_core.auto import RendererSpec, register_renderer
from hedron_core.identifiers import content_digest
from hedron_core.plugins import PluginCapabilities, PluginContext, PluginMeta
from hedron_core.registry import register_asset, register_browser_module, register_component

_ROOT = Path(__file__).resolve().parent
_PLOTLY_HOST = _ROOT / "assets" / "plotly" / "host.js"
_VEGA_HOST = _ROOT / "assets" / "vega" / "host.js"

PLUGIN_META = PluginMeta(
    name="hedron_charts",
    version="0.6.0",
    distribution="hedron-charts",
    hedron_version=">=0.6,<0.7",
    capabilities=PluginCapabilities(
        python=True,
        styles=True,
        assets=True,
        browser_js=True,
        explorer_panels=True,
    ),
)


def _factory_matplotlib(value: Any) -> Any:
    return MatplotlibChart(value, title="Chart", description="Auto-rendered Matplotlib figure")


def _factory_plotly(value: Any) -> Any:
    return PlotlyChart(value, description="Auto-rendered Plotly figure")


def _factory_altair(value: Any) -> Any:
    return AltairChart(value, description="Auto-rendered Altair chart")


def register(ctx: PluginContext) -> None:
    for cls in (LineChart, MatplotlibChart, PlotlyChart, AltairChart):
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

    if _PLOTLY_HOST.is_file():
        register_browser_module(
            logical_id="hedron-charts:plotly-host",
            tag_name="hedron-plotly-chart",
            module_path=str(_PLOTLY_HOST),
            observed_attributes=("data-hedron-payload",),
            events=(),
            shadow_dom=False,
            htmx_lifecycle=True,
        )
    if _VEGA_HOST.is_file():
        register_browser_module(
            logical_id="hedron-charts:vega-host",
            tag_name="hedron-vega-chart",
            module_path=str(_VEGA_HOST),
            observed_attributes=("data-hedron-payload",),
            events=(),
            shadow_dom=False,
            htmx_lifecycle=True,
        )

    # Replace chart-stub with real adapters when package is loaded.
    register_renderer(
        RendererSpec(
            name="matplotlib",
            priority=910,
            predicate=MatplotlibAdapter().supports,
            optional_package="hedron-charts[matplotlib]",
            explanation="Matplotlib Figure → MatplotlibChart",
            factory=_factory_matplotlib,
        )
    )
    register_renderer(
        RendererSpec(
            name="plotly",
            priority=920,
            predicate=PlotlyAdapter().supports,
            optional_package="hedron-charts[plotly]",
            explanation="Plotly figure → PlotlyChart",
            factory=_factory_plotly,
        )
    )
    register_renderer(
        RendererSpec(
            name="altair",
            priority=915,
            predicate=AltairAdapter().supports,
            optional_package="hedron-charts[altair]",
            explanation="Altair/Vega-Lite → AltairChart",
            factory=_factory_altair,
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
