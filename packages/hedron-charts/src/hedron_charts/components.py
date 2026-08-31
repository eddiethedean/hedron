"""Public chart components."""

from __future__ import annotations

import html as html_stdlib
from collections.abc import Mapping, Sequence
from typing import Any

from hedron_charts.adapters import (
    AltairAdapter,
    MatplotlibAdapter,
    PlotlyAdapter,
    _fallback_table,  # pyright: ignore[reportPrivateUsage]
    compile_figure,
)
from hedron_charts.limits import (
    accessibility_or_raise,
    ensure_limits,
    redact_rows,
    reject_active_svg,
)
from hedron_core.builtins.content import Text
from hedron_core.component import Component, NodeLike
from hedron_core.html import html
from hedron_core.models import Props
from hedron_core.typing_aliases import JsonValue
from hedron_core.visualization import VisualizationLimits


def _coerce_float(value: object, *, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return float(value)
        return float(str(value))
    except (TypeError, ValueError, OverflowError):
        return default


__all__ = [
    "AltairChart",
    "AreaChart",
    "BarChart",
    "Chart",
    "LineChart",
    "MatplotlibChart",
    "PlotlyChart",
    "ScatterChart",
]

# Re-export advanced Chart for components consumers.
from hedron_charts.element import Chart  # noqa: E402


def _xy_fallback_figure(  # pyright: ignore[reportUnusedFunction]
    *,
    data: Sequence[Mapping[str, JsonValue]],
    x: str,
    y: str,
    title: str,
    description: str | None,
    alt: str | None,
    waiver: str | None,
    limits: VisualizationLimits | None,
    kind: str,
) -> NodeLike:
    acc = accessibility_or_raise(
        title=title,
        description=description,
        alt=alt,
        waiver=waiver,
        tabular_fallback=redact_rows(data),
    )
    ensure_limits(data, None, limits=limits)
    try:
        import matplotlib

        matplotlib.use("Agg", force=False)
        import matplotlib.pyplot as plt

        fig: object
        ax: object
        fig, ax = plt.subplots()  # type: ignore[reportUnknownMemberType]
        axes: Any = ax
        xs_raw = [row.get(x) for row in data]
        ys = [_coerce_float(row.get(y)) for row in data]
        labels = [str(v) for v in xs_raw]
        numeric_xs: list[float] = []
        categorical = False
        for raw in xs_raw:
            try:
                try:
                    numeric_xs.append(float(raw))  # type: ignore[arg-type]
                except OverflowError:
                    numeric_xs.append(0.0)
            except (TypeError, ValueError):
                categorical = True
                break
        if kind == "bar" or categorical:
            ax_x = list(range(len(ys)))
            if kind == "bar":
                axes.bar(ax_x, ys)
            elif kind == "scatter":
                axes.scatter(ax_x, ys)
            elif kind == "area":
                axes.fill_between(ax_x, ys)
            else:
                axes.plot(ax_x, ys)
            axes.set_xticks(ax_x)
            axes.set_xticklabels(labels)
        elif kind == "scatter":
            axes.scatter(numeric_xs, ys)
        elif kind == "area":
            axes.fill_between(numeric_xs, ys)
        else:
            axes.plot(numeric_xs, ys)
        axes.set_xlabel(x)
        axes.set_ylabel(y)
        axes.set_title(acc.title)
        adapter = MatplotlibAdapter()
        output = adapter.compile(fig, accessibility=acc, limits=limits)
        plt.close(fig)
        return adapter.render_node(output)
    except ImportError:
        xs_raw = [row.get(x) for row in data]
        ys = [_coerce_float(row.get(y)) for row in data]
        numeric_xs: list[float] = []
        categorical = False
        for raw in xs_raw:
            try:
                try:
                    numeric_xs.append(float(raw))  # type: ignore[arg-type]
                except OverflowError:
                    numeric_xs.append(0.0)
            except (TypeError, ValueError):
                categorical = True
                break
        y_min = min(0.0, min(ys)) if ys else 0.0
        y_max = max(0.0, max(ys)) if ys else 1.0
        y_span = y_max - y_min or 1.0
        width, height = 320, 160
        shapes: list[str] = []
        use_index = kind == "bar" or categorical or not numeric_xs
        if use_index:
            xs_plot = list(range(len(ys)))
            min_x, max_x = 0.0, float(max(len(ys) - 1, 1))
        else:
            xs_plot = numeric_xs
            min_x = min(numeric_xs)
            max_x = max(numeric_xs)
            if max_x == min_x:
                max_x = min_x + 1.0

        def _px(xv: float) -> float:
            return ((xv - min_x) / (max_x - min_x)) * (width - 20) + 10

        def _py(yv: float) -> float:
            t = (yv - y_min) / y_span
            raw = height - 10 - t * (height - 20)
            return min(height - 10, max(10.0, raw))

        zero_y = _py(0.0)
        if kind == "bar":
            bar_w = (width - 20) / max(len(ys), 1)
            for i, yv in enumerate(ys):
                top = _py(yv)
                y_rect = min(zero_y, top)
                bh = abs(zero_y - top)
                shapes.append(
                    f'<rect x="{10 + i * bar_w:.1f}" y="{y_rect:.1f}" '
                    f'width="{max(bar_w - 2, 1):.1f}" '
                    f'height="{max(bh, 0.0):.1f}" fill="currentColor"/>'
                )
        elif kind == "scatter":
            for xv, yv in zip(xs_plot, ys, strict=False):
                px = _px(float(xv))
                py = _py(yv)
                shapes.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="currentColor"/>')
        else:
            points: list[str] = []
            for xv, yv in zip(xs_plot, ys, strict=False):
                px = _px(float(xv))
                py = _py(yv)
                points.append(f"{px:.1f},{py:.1f}")
            poly = " ".join(points)
            if kind == "area" and points:
                shapes.append(
                    f'<polygon fill="currentColor" fill-opacity="0.3" '
                    f'points="{_px(float(xs_plot[0])):.1f},{zero_y:.1f} {poly} '
                    f'{_px(float(xs_plot[-1])):.1f},{zero_y:.1f}"/>'
                )
            shapes.append(
                f'<polyline fill="none" stroke="currentColor" stroke-width="2" points="{poly}"/>'
            )
        title_text = html_stdlib.escape(acc.title, quote=False)
        label_text = html_stdlib.escape(acc.alt or acc.title, quote=True)
        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 160" '
            f'role="img" aria-label="{label_text}"><title>{title_text}</title>'
            f"{''.join(shapes)}</svg>"
        )
        from hedron_core.security import TrustedHtml

        reject_active_svg(svg)
        return html.figure(
            html.h2(acc.title),
            html.p(acc.description or ""),
            html.raw(TrustedHtml.reviewed(svg, source=f"hedron-charts:{kind}-fallback")),
            _fallback_table(acc.tabular_fallback) if acc.tabular_fallback else Text(""),
            class_=f"hedron-chart hedron-chart-{kind}",
        )


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
        data: Sequence[Mapping[str, JsonValue]],
        *,
        x: str,
        y: str,
        title: str,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        limits: VisualizationLimits | None = None,
        **kwargs: object,
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

    def render(self) -> NodeLike:
        from hedron_charts.element import chart_from_beginner

        accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
            tabular_fallback=redact_rows(self._data),
        )
        ensure_limits(self._data, None, limits=self._limits)
        return chart_from_beginner(
            kind="line",
            data=self._data,
            x=self._x,
            y=self._y,
            title=self.props.title,
            description=self.props.description
            or self.props.alt
            or self.props.waiver
            or self.props.title,
        ).render()


class AreaChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "AreaChart"
    props_type = _ChartProps

    def __init__(
        self,
        data: Sequence[Mapping[str, JsonValue]],
        *,
        x: str,
        y: str,
        title: str,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        limits: VisualizationLimits | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(title=title, description=description, alt=alt, waiver=waiver, **kwargs)
        self._data = list(data)
        self._x = x
        self._y = y
        self._limits = limits

    def render(self) -> NodeLike:
        from hedron_charts.element import chart_from_beginner

        accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
            tabular_fallback=redact_rows(self._data),
        )
        ensure_limits(self._data, None, limits=self._limits)
        return chart_from_beginner(
            kind="area",
            data=self._data,
            x=self._x,
            y=self._y,
            title=self.props.title,
            description=self.props.description
            or self.props.alt
            or self.props.waiver
            or self.props.title,
        ).render()


class BarChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "BarChart"
    props_type = _ChartProps

    def __init__(
        self,
        data: Sequence[Mapping[str, JsonValue]],
        *,
        x: str,
        y: str,
        title: str,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        limits: VisualizationLimits | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(title=title, description=description, alt=alt, waiver=waiver, **kwargs)
        self._data = list(data)
        self._x = x
        self._y = y
        self._limits = limits

    def render(self) -> NodeLike:
        from hedron_charts.element import chart_from_beginner

        accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
            tabular_fallback=redact_rows(self._data),
        )
        ensure_limits(self._data, None, limits=self._limits)
        return chart_from_beginner(
            kind="bar",
            data=self._data,
            x=self._x,
            y=self._y,
            title=self.props.title,
            description=self.props.description
            or self.props.alt
            or self.props.waiver
            or self.props.title,
        ).render()


class ScatterChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "ScatterChart"
    props_type = _ChartProps

    def __init__(
        self,
        data: Sequence[Mapping[str, JsonValue]],
        *,
        x: str,
        y: str,
        title: str,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        limits: VisualizationLimits | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(title=title, description=description, alt=alt, waiver=waiver, **kwargs)
        self._data = list(data)
        self._x = x
        self._y = y
        self._limits = limits

    def render(self) -> NodeLike:
        from hedron_charts.element import chart_from_beginner

        accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
            tabular_fallback=redact_rows(self._data),
        )
        ensure_limits(self._data, None, limits=self._limits)
        return chart_from_beginner(
            kind="scatter",
            data=self._data,
            x=self._x,
            y=self._y,
            title=self.props.title,
            description=self.props.description
            or self.props.alt
            or self.props.waiver
            or self.props.title,
        ).render()


class MatplotlibChart(Component[_ChartProps]):
    distribution = "hedron-charts"
    logical_name = "MatplotlibChart"
    props_type = _ChartProps

    def __init__(
        self,
        figure: object,
        *,
        title: str | None = None,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        fmt: str = "svg",
        **kwargs: object,
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

    def render(self) -> NodeLike:
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
        figure: object,
        *,
        title: str | None = None,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            title=title or "Chart",
            description=description,
            alt=alt,
            waiver=waiver,
            **kwargs,
        )
        self._figure = figure

    def render(self) -> NodeLike:
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
        chart: object,
        *,
        title: str | None = None,
        description: str | None = None,
        alt: str | None = None,
        waiver: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(
            title=title or "Chart",
            description=description,
            alt=alt,
            waiver=waiver,
            **kwargs,
        )
        self._chart = chart

    def render(self) -> NodeLike:
        adapter = AltairAdapter()
        acc = accessibility_or_raise(
            title=self.props.title,
            description=self.props.description,
            alt=self.props.alt,
            waiver=self.props.waiver,
        )
        output = adapter.compile(self._chart, accessibility=acc)
        return adapter.render_node(output)
