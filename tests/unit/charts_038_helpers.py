"""Shared helpers for phase 0.38 chart tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hedron_charts.compile import beginner_to_spec, compile_chart
from hedron_charts.spec import ChartSpec

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "charts_038"
DATASETS = json.loads((FIXTURES / "datasets.json").read_text(encoding="utf-8"))


def sample_rows(name: str = "numeric") -> list[dict[str, Any]]:
    rows = DATASETS[name]
    if name == "dense":
        return [{"x": i, "y": (i % 17) + 1} for i in range(3000)]
    assert isinstance(rows, list)
    return list(rows)


def sample_spec(**kwargs: Any) -> ChartSpec:
    data = kwargs.pop("data", sample_rows())
    kind = kwargs.pop("kind", "line")
    return beginner_to_spec(
        kind=kind,
        data=data,
        x=kwargs.pop("x", "x"),
        y=kwargs.pop("y", "y"),
        title=kwargs.pop("title", "Sample"),
        description=kwargs.pop("description", "Sample chart"),
        color=kwargs.pop("color", None),
    )


def sample_plan(**kwargs: Any):
    return compile_chart(sample_spec(**kwargs))
