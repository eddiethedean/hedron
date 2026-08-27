from __future__ import annotations

import tomllib
from pathlib import Path

from hedron.plugins import compatible_hedron_version
from hedron_charts.plugin import PLUGIN_META
from hedron_core.visualization import ChartEvent, validate_chart_event

ROOT = Path(__file__).resolve().parents[2]


def test_chart_event_kinds_and_plugin_version() -> None:
    release = tomllib.loads((ROOT / "docs" / "release.toml").read_text(encoding="utf-8"))["release"]
    train = str(release["development_version"])
    for kind in ("hover", "click", "box", "lasso", "relayout", "restyle", "extend", "prepend"):
        validate_chart_event(ChartEvent(kind=kind, trace_id="t0", payload={}))
        assert compatible_hedron_version(PLUGIN_META.hedron_version, train)
