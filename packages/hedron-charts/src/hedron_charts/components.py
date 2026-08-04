"""Public chart components."""

from __future__ import annotations

import html as html_stdlib
from collections.abc import Mapping, Sequence
from typing import Any

from hedron_charts.adapters import (
    AltairAdapter,
    MatplotlibAdapter,
    PlotlyAdapter,
    _fallback_table,
    compile_figure,
)
from hedron_charts.limits import (
    accessibility_or_raise,
    ensure_limits,
    redact_rows,
    reject_active_svg,
)
from hedron_core.builtins.content import Text
from hedron_core.component import Component
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.visualization import VisualizationLimits


def _coerce_float(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


__all__ = ["AltairChart", "LineChart", "MatplotlibChart", "PlotlyChart"]


class _ChartProps(Props):
    title: str = ""
    description: str | None = None
    alt: str | None = None
    waiver: str | None = None


class LineChart(Component[_ChartProps]):
    """Beginner backend-neutral line chart over row mappings."""

    distribution = "hedron-charts"
    logical_name = "LineChart"
    props_type = _ChartProps

    def __init__(
        self,
        data: Sequence[Mapping[str, Any]],
        *,
        x: str,
        y: str,
        title: str,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        limits: VisualizationLimits | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title,
            description=description,
            alt=alt,
            waiver=waiver,
            **kwargs,
        )
        self._data = list(data)
        self._x = x
        self._y = y
        self._limits = limits

    def render(self) -> Any:
        acc = accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
            tabular_fallback=redact_rows(self._data),
        )
        ensure_limits(self._data, None, limits=self._limits)
        # Prefer matplotlib when available; otherwise render accessible SVG polyline.
        try:
            import matplotlib

            matplotlib.use("Agg", force=False)
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            xs_raw = [row.get(self._x) for row in self._data]
            ys = [_coerce_float(row.get(self._y)) for row in self._data]
            numeric_xs: list[float] = []
            categorical = False
            for raw in xs_raw:
                try:
                    numeric_xs.append(float(raw))  # type: ignore[arg-type]
                except (TypeError, ValueError):
                    categorical = True
                    break
            if categorical:
                ax.plot(list(range(len(ys))), ys)
                ax.set_xticks(list(range(len(ys))))
                ax.set_xticklabels([str(x) for x in xs_raw])
            else:
                ax.plot(numeric_xs, ys)
            ax.set_xlabel(self._x)
            ax.set_ylabel(self._y)
            ax.set_title(acc.title)
            adapter = MatplotlibAdapter()
            output = adapter.compile(fig, accessibility=acc, limits=self._limits)
            plt.close(fig)
            return adapter.render_node(output)
        except ImportError:
            points = []
            if self._data:
                ys = [_coerce_float(row.get(self._y)) for row in self._data]
                max_y = max(ys) or 1.0
                width = 320
                height = 160
                for i, y in enumerate(ys):
                    px = (i / max(len(ys) - 1, 1)) * (width - 20) + 10
                    py = height - 10 - (y / max_y) * (height - 20)
                    points.append(f"{px:.1f},{py:.1f}")
                poly = " ".join(points)
                title_text = html_stdlib.escape(acc.title, quote=False)
                label_text = html_stdlib.escape(acc.alt or acc.title, quote=True)
                svg = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 160" '
                    f'role="img" aria-label="{label_text}">'
                    f"<title>{title_text}</title>"
                    f'<polyline fill="none" stroke="currentColor" '
                    f'stroke-width="2" points="{poly}"/>'
                    f"</svg>"
                )
                from hedron_core.security import TrustedHtml

                reject_active_svg(svg)
                return html.figure(
                    html.h2(acc.title),
                    html.p(acc.description or ""),
                    html.raw(TrustedHtml.reviewed(svg, source="hedron-charts:line-fallback")),
                    _fallback_table(acc.tabular_fallback) if acc.tabular_fallback else Text(""),
                    class_="hedron-chart hedron-chart-line",
                )
            return html.figure(html.h2(acc.title), html.p("No data"), class_="hedron-chart")


class MatplotlibChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "MatplotlibChart"
    props_type = _ChartProps

    def __init__(
        self,
        figure: Any,
        *,
        title: str | None = None,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        fmt: str = "svg",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title or "Chart",
            description=description,
            alt=alt,
            waiver=waiver,
            **kwargs,
        )
        self._figure = figure
        self._fmt = fmt

    def render(self) -> Any:
        adapter = MatplotlibAdapter()
        acc = accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
        )
        output = adapter.compile(self._figure, accessibility=acc, fmt=self._fmt)
        return adapter.render_node(output)


class PlotlyChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "PlotlyChart"
    props_type = _ChartProps

    def __init__(
        self,
        figure: Any,
        *,
        title: str | None = None,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title or "Chart",
            description=description,
            alt=alt,
            waiver=waiver,
            **kwargs,
        )
        self._figure = figure

    def render(self) -> Any:
        adapter, output = compile_figure(
            self._figure,
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
        )
        if not isinstance(adapter, PlotlyAdapter):
            adapter = PlotlyAdapter()
            output = adapter.compile(
                self._figure,
                accessibility=accessibility_or_raise(
                    title=self.props.title,
                    description=self.props.description,
                    alt=self.props.alt,
                    waiver=self.props.waiver,
                ),
            )
        return adapter.render_node(output)


class AltairChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "AltairChart"
    props_type = _ChartProps

    def __init__(
        self,
        chart: Any,
        *,
        title: str | None = None,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            title=title or "Chart",
            description=description,
            alt=alt,
            waiver=waiver,
            **kwargs,
        )
        self._chart = chart

    def render(self) -> Any:
        adapter = AltairAdapter()
        acc = accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
        )
        output = adapter.compile(self._chart, accessibility=acc)
        return adapter.render_node(output)
