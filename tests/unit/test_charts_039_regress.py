"""REGRESS-039 chart adapter fixes (#73, #84, #118, #192, #194)."""

from __future__ import annotations

import json

import pytest

from hedron_charts.host_render import extract_folium_payload, extract_pydeck_payload
from hedron_charts.limits import redact_rows
from hedron_charts.optional_adapters import GreatTablesAdapter, PyDeckAdapter, ThreeJsAdapter
from hedron_core.diagnostics import HedronError
from hedron_core.visualization import ChartAccessibility, VisualizationLimits


def test_039_great_tables_list_path_enforces_payload_bytes() -> None:
    acc = ChartAccessibility(title="t", alt="a")
    rows = [{"a": "x" * 5_000}]
    with pytest.raises(HedronError, match="HED-CHART-0003|payload"):
        GreatTablesAdapter().compile(
            rows,
            accessibility=acc,
            limits=VisualizationLimits(max_rows=100, max_payload_bytes=1000),
        )


def test_039_great_tables_payload_bytes_match_redacted_body() -> None:
    acc = ChartAccessibility(title="t", alt="a")
    rows = [{"password": "hunter2", "notes": "ok"}]
    out = GreatTablesAdapter().compile(rows, accessibility=acc)
    assert out.payload_bytes == len(out.body.encode("utf-8"))
    parsed = json.loads(out.body)
    assert parsed[0]["password"] == "***"
    assert parsed[0]["notes"] == "ok"


def test_039_pydeck_maps_view_state_to_maplibre_contract() -> None:
    acc = ChartAccessibility(title="Map", description="d")
    out = PyDeckAdapter().compile(
        {
            "initial_view_state": {"longitude": -122.4, "latitude": 37.8, "zoom": 11},
            "layers": [],
        },
        accessibility=acc,
        limits=VisualizationLimits(),
    )
    body = json.loads(out.body)
    assert body["center"] == [37.8, -122.4]
    assert body["zoom"] == 11
    assert "initial_view_state" not in body


def test_039_pydeck_rejects_unsupported_layers() -> None:
    with pytest.raises(TypeError, match="Unsupported PyDeck|MapLibre"):
        extract_pydeck_payload(
            {
                "initial_view_state": {"longitude": 0, "latitude": 0, "zoom": 1},
                "layers": [{"data": {"not": "geojson"}}],
            }
        )


def test_039_folium_preserves_zoom_zero() -> None:
    payload = extract_folium_payload({"type": "folium", "center": [0, 0], "zoom": 0})
    assert payload["zoom"] == 0


def test_039_redact_rows_exact_keys_only() -> None:
    rows = [{"secretary": "bob", "password": "x", "notes": "ok", "secret": "s"}]
    cleaned = redact_rows(rows)
    assert cleaned[0]["secretary"] == "bob"
    assert cleaned[0]["password"] == "***"
    assert cleaned[0]["secret"] == "***"
    assert cleaned[0]["notes"] == "ok"


def test_039_threejs_rejects_path_traversal() -> None:
    acc = ChartAccessibility(title="m", description="d")
    with pytest.raises(ValueError, match="traversal"):
        ThreeJsAdapter().compile(
            {"model_url": "../../../secret/model.glb", "bytes": 100},
            accessibility=acc,
        )
    # Simple local asset names remain allowed.
    ThreeJsAdapter().compile({"model_url": "model.glb", "bytes": 10}, accessibility=acc)


def test_039_chart_divide_zero_is_null() -> None:
    from hedron_charts.compile import compile_chart

    plan = compile_chart(
        {
            "data": {"rows": ({"a": 10, "b": 0},)},
            "marks": ({"type": "point"},),
            "transforms": ({"op": "divide", "as": "q", "params": {"args": ["a", "b"]}},),
            "accessibility": {"title": "T", "description": "D"},
        }
    )
    assert plan.transformed_rows[0]["q"] is None
