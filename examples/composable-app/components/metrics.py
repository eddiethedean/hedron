"""Reusable metric components for the overview page."""

from __future__ import annotations

from collections.abc import Sequence

from hedron import Card, Grid, Metric

MetricValue = tuple[str, str, str]


def metrics_overview(values: Sequence[MetricValue], *, class_: str | None = None) -> Grid:
    """Build a responsive metric grid from application data."""
    return Grid(
        *(
            Card(Metric(label, value, delta=delta, delta_tone="up"))
            for label, value, delta in values
        ),
        columns={"base": 1, "md": 3},
        class_=class_,
    )
