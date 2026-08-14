"""Closed ChartSpec operator catalog (RFC-0069 / CHART_SPEC.md)."""

from __future__ import annotations

from typing import Final

ARITHMETIC: Final[frozenset[str]] = frozenset(
    {
        "add",
        "subtract",
        "multiply",
        "divide",
        "negate",
        "abs",
        "round",
        "floor",
        "ceil",
        "min",
        "max",
        "clamp",
        "coalesce",
    }
)
COMPARE_LOGIC: Final[frozenset[str]] = frozenset(
    {
        "eq",
        "ne",
        "lt",
        "le",
        "gt",
        "ge",
        "in",
        "not_in",
        "is_null",
        "is_not_null",
        "and",
        "or",
        "not",
    }
)
STRING_OPS: Final[frozenset[str]] = frozenset({"concat", "length", "lower", "upper"})
TEMPORAL: Final[frozenset[str]] = frozenset(
    {"year", "month", "day", "hour", "minute", "second", "date_trunc"}
)
AGGREGATE: Final[frozenset[str]] = frozenset(
    {
        "count",
        "count_distinct",
        "sum",
        "mean",
        "median",
        "min",
        "max",
        "stdev",
        "first",
        "last",
    }
)
WINDOW: Final[frozenset[str]] = frozenset(
    {
        "lag",
        "lead",
        "rank",
        "dense_rank",
        "row_number",
        "running_sum",
        "running_mean",
    }
)
STRUCTURAL: Final[frozenset[str]] = frozenset(
    {"filter", "aggregate", "bin", "stack", "sort", "fold", "sample"}
)

ALLOWED_OPERATORS: Final[frozenset[str]] = (
    ARITHMETIC | COMPARE_LOGIC | STRING_OPS | TEMPORAL | AGGREGATE | WINDOW | STRUCTURAL
)

SUPPORTED_MARKS: Final[frozenset[str]] = frozenset(
    {"line", "area", "bar", "point", "rect", "rule", "box", "arc", "ohlc", "candlestick"}
)
SUPPORTED_SCALES: Final[frozenset[str]] = frozenset(
    {
        "linear",
        "log",
        "symlog",
        "power",
        "time",
        "utc",
        "ordinal",
        "point",
        "band",
        "quantized",
    }
)
SUPPORTED_ENCODINGS: Final[frozenset[str]] = frozenset(
    {
        "x",
        "y",
        "x2",
        "y2",
        "color",
        "size",
        "opacity",
        "shape",
        "stroke",
        "detail",
        "group",
        "order",
        "tooltip",
        "text",
        "open",
        "high",
        "low",
        "close",
    }
)
EVENT_KINDS: Final[frozenset[str]] = frozenset(
    {
        "inspect",
        "focus",
        "select",
        "legend_filter",
        "brush",
        "zoom",
        "pan",
        "reset",
        "crosshair",
        "drill_intent",
    }
)

# Map legacy 0.1 ChartEvent kinds → 0.38 kinds (or fail-closed codes).
LEGACY_EVENT_MAP: Final[dict[str, str]] = {
    "hover": "inspect",
    "click": "select",
    "click-annotation": "inspect",
    "box": "brush",
    "lasso": "brush",
    "relayout": "zoom",
    "restyle": "legend_filter",
    "legend": "legend_filter",
}
LEGACY_EVENT_FAIL: Final[frozenset[str]] = frozenset({"extend", "prepend"})
