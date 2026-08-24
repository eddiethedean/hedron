"""Theme-owned visualization palette and accessibility presentation primitives."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from hedron_core.theme import Theme, default_theme

__all__ = [
    "VISUALIZATION_ROLES",
    "VisualizationPalette",
    "VisualizationSeries",
    "emit_visualization_theme_css",
    "resolve_visualization_theme",
]

VISUALIZATION_ROLES = (
    "series-1",
    "series-2",
    "series-3",
    "series-4",
    "series-5",
    "series-6",
    "series-7",
    "series-8",
    "axis",
    "grid",
    "label",
    "selection",
    "focus",
    "surface",
    "tooltip-bg",
    "tooltip-fg",
)

_DEFAULT_SERIES = (
    "#2563eb",
    "#dc2626",
    "#15803d",
    "#a16207",
    "#7e22ce",
    "#0e7490",
    "#be185d",
    "#475569",
)
_PATTERNS = ("solid", "dash", "dot", "dash-dot", "long-dash", "dense-dot", "wide-dot", "double")
_MARKERS = ("circle", "square", "triangle", "diamond", "cross", "plus", "star", "hexagon")
_SAFE_MODE = re.compile(r"^[a-z][a-z0-9-]*$")


@dataclass(frozen=True, slots=True)
class VisualizationSeries:
    index: int
    role: str
    color: str
    pattern: str
    marker: str

    def to_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "role": self.role,
            "color": self.color,
            "pattern": self.pattern,
            "marker": self.marker,
        }


@dataclass(frozen=True, slots=True)
class VisualizationPalette:
    """Resolved palette shared by chart renderers and semantic fallbacks."""

    mode: str
    accessibility_mode: str
    roles: Mapping[str, str]
    series: tuple[VisualizationSeries, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "hedron.visualization-theme/1",
            "mode": self.mode,
            "accessibility_mode": self.accessibility_mode,
            "roles": dict(self.roles),
            "series": [item.to_dict() for item in self.series],
        }


def _theme_value(theme: Theme, key: str, mode: str, fallback: str) -> str:
    values = dict(theme.tokens)
    values.update(theme.modes.get(mode, {}))
    return values.get(key, fallback)


def resolve_visualization_theme(
    theme: Theme | None = None,
    *,
    mode: str = "light",
    accessibility_mode: str = "none",
    series_count: int = 8,
) -> VisualizationPalette:
    """Resolve semantic series, surface, and interaction roles from a Theme.

    ``forced-colors`` intentionally uses system colors and retains patterns and
    markers, so meaning never depends on hue alone.
    """
    if not _SAFE_MODE.fullmatch(mode):
        raise ValueError("visualization mode must be a safe identifier")
    if accessibility_mode not in {
        "none",
        "forced-colors",
        "print",
        "reduced-transparency",
        "high-contrast",
    }:
        raise ValueError("unsupported visualization accessibility mode")
    if not 1 <= series_count <= 8:
        raise ValueError("series_count must be between 1 and 8")
    source = theme or default_theme()
    roles: dict[str, str] = {
        "axis": _theme_value(
            source, "chart.axis", mode, _theme_value(source, "color.muted", mode, "#64748b")
        ),
        "grid": _theme_value(
            source, "chart.grid", mode, "#cbd5e1" if mode != "dark" else "#475569"
        ),
        "label": _theme_value(
            source, "chart.label", mode, _theme_value(source, "color.fg", mode, "#172033")
        ),
        "selection": _theme_value(
            source, "chart.selection", mode, _theme_value(source, "color.accent", mode, "#2563eb")
        ),
        "focus": _theme_value(
            source, "chart.focus", mode, _theme_value(source, "color.focus", mode, "#2563eb")
        ),
        "surface": _theme_value(
            source, "chart.surface", mode, _theme_value(source, "color.surface", mode, "#ffffff")
        ),
        "tooltip-bg": _theme_value(
            source, "chart.tooltip-bg", mode, _theme_value(source, "color.fg", mode, "#172033")
        ),
        "tooltip-fg": _theme_value(
            source, "chart.tooltip-fg", mode, _theme_value(source, "color.bg", mode, "#ffffff")
        ),
    }
    if accessibility_mode == "forced-colors":
        roles.update(
            {
                "axis": "CanvasText",
                "grid": "GrayText",
                "label": "CanvasText",
                "selection": "Highlight",
                "focus": "Highlight",
                "surface": "Canvas",
                "tooltip-bg": "CanvasText",
                "tooltip-fg": "Canvas",
            }
        )
    elif accessibility_mode == "print":
        roles.update(
            {
                "axis": "#000000",
                "grid": "#666666",
                "label": "#000000",
                "selection": "#000000",
                "focus": "#000000",
                "surface": "#ffffff",
                "tooltip-bg": "#ffffff",
                "tooltip-fg": "#000000",
            }
        )
    series: list[VisualizationSeries] = []
    for index in range(series_count):
        role = f"series-{index + 1}"
        fallback = _DEFAULT_SERIES[index]
        color = _theme_value(source, f"chart.{role}", mode, fallback)
        if accessibility_mode == "forced-colors":
            color = "CanvasText"
        roles[role] = color
        series.append(
            VisualizationSeries(index + 1, role, color, _PATTERNS[index], _MARKERS[index])
        )
    return VisualizationPalette(mode, accessibility_mode, roles, tuple(series))


def emit_visualization_theme_css(
    theme: Theme | None = None,
    *,
    mode: str = "light",
) -> str:
    """Emit one CSS contract used by SVG, Canvas, table, and print fallbacks."""
    palette = resolve_visualization_theme(theme, mode=mode)
    lines = ["@layer tokens {", ":root {"]
    for role in VISUALIZATION_ROLES:
        lines.append(f"  --hedron-chart-{role}: {palette.roles[role]};")
    for item in palette.series:
        lines.append(f"  --hedron-chart-pattern-{item.role}: {item.pattern};")
        lines.append(f"  --hedron-chart-marker-{item.role}: {item.marker};")
    lines.extend(["}", "}", "@media (forced-colors: active) {", "  :root {"])
    forced = resolve_visualization_theme(theme, mode=mode, accessibility_mode="forced-colors")
    for role in VISUALIZATION_ROLES:
        lines.append(f"    --hedron-chart-{role}: {forced.roles[role]};")
    lines.extend(["  }", "}", "@media print {", "  :root {"])
    printed = resolve_visualization_theme(theme, mode=mode, accessibility_mode="print")
    for role in VISUALIZATION_ROLES:
        lines.append(f"    --hedron-chart-{role}: {printed.roles[role]};")
    lines.extend(
        [
            "  }",
            "}",
            "@media (prefers-reduced-transparency: reduce) {",
            "  hedron-chart { backdrop-filter: none; }",
            "}",
        ]
    )
    return "\n".join(lines) + "\n"
