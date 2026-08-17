"""PERF-047 measured budgets and zero cost when uninstalled."""

from __future__ import annotations

import ast
import time
from pathlib import Path

from hedron_maps import compile_map
from hedron_maps.limits import LIMITS, MAX_FEATURES, MAX_PLAN_BYTES
from hedron_maps.spec import AccessibilityDef, GeoJSONLayer, MapSpec, OpenStreetMap, ViewState


def test_compile_500_features_stays_within_budget() -> None:
    features = [
        {
            "type": "Feature",
            "properties": {"name": f"f{i}"},
            "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        }
        for i in range(MAX_FEATURES)
    ]
    spec = MapSpec(
        basemap=OpenStreetMap.standard(),
        layers=(GeoJSONLayer(data={"type": "FeatureCollection", "features": features}),),
        view=ViewState(zoom=2),
        accessibility=AccessibilityDef(title="Perf", description="500 points"),
    )
    started = time.perf_counter()
    plan = compile_map(spec)
    elapsed = time.perf_counter() - started
    import json

    size = len(json.dumps(plan.to_json_dict(), separators=(",", ":")).encode("utf-8"))
    assert size <= MAX_PLAN_BYTES
    assert elapsed < 2.0
    assert plan.limits == LIMITS


def test_core_has_zero_maps_import_cost() -> None:
    tree = ast.parse(
        Path("packages/hedron-core/src/hedron_core/__init__.py").read_text(encoding="utf-8")
    )
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not any("hedron_maps" in name for name in imported)
    flagship = Path("packages/hedron/src/hedron/__init__.py").read_text(encoding="utf-8")
    assert "hedron_maps" not in flagship
    assert LIMITS["maps_per_page"] == 8
    assert LIMITS["tile_concurrency"] == 8
    assert LIMITS["workers"] == 1
