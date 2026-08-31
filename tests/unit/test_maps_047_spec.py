"""SPEC-047 MapSpec / MapPlan / compile_map."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from hedron_core import HedronError
from hedron_core.codes import HED_MAP_SPEC_0001, HED_MAP_SPEC_0002, HED_MAP_SPEC_0004
from hedron_maps import Map, MapPlan, MapSpec, OpenStreetMap, compile_map
from hedron_maps.limits import LIMITS, MAX_FEATURES
from hedron_maps.spec import AccessibilityDef, GeoJSONLayer, MarkerLayer, ViewState

PORTABLE = (
    Path("packages/hedron-maps/src/hedron_maps/spec.py"),
    Path("packages/hedron-maps/src/hedron_maps/compile.py"),
    Path("packages/hedron-maps/src/hedron_maps/limits.py"),
    Path("packages/hedron-maps/src/hedron_maps/element.py"),
    Path("packages/hedron-maps/src/hedron_maps/interaction.py"),
)


def test_compile_map_is_deterministic_and_inert() -> None:
    spec = MapSpec(
        basemap=OpenStreetMap.standard(),
        view=ViewState(center=(37.77, -122.42), zoom=11),
        accessibility=AccessibilityDef(title="Bay", description="Test map"),
    )
    first = compile_map(spec)
    second = compile_map(spec)
    assert isinstance(first, MapPlan)
    assert first.plan_fingerprint == second.plan_fingerprint
    assert first.plan_fingerprint != first.spec_fingerprint
    dumped = first.to_json_dict()
    assert "Bearer " not in str(dumped)
    assert first.source_kind == "openstreetmap-standard"
    assert first.preset_id == "openstreetmap-standard"
    assert "© OpenStreetMap contributors" in first.attribution
    assert first.limits["geojson_features"] == MAX_FEATURES
    assert first.renderer["version"] == "5.6.1"
    assert first.renderer["public_python_type"] is False
    assert first.fallback["alternative_class"] == "hedron-map-alternative"


def test_unknown_spec_field_fails() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            {
                "schema_version": 1,
                "accessibility": {"title": "T", "description": "D"},
                "callback": "nope",
            }
        )
    assert exc.value.diagnostic.code == HED_MAP_SPEC_0001


def test_prototype_pollution_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(
            {
                "schema_version": 1,
                "accessibility": {"title": "T", "description": "D"},
                "theme": {"mode": "light", "tokens": {"__proto__": "x"}},
            }
        )
    assert exc.value.diagnostic.code == HED_MAP_SPEC_0001


def test_missing_title_rejected() -> None:
    with pytest.raises(HedronError) as exc:
        compile_map(MapSpec(accessibility=AccessibilityDef(title=" ", description="D")))
    assert exc.value.diagnostic.code == HED_MAP_SPEC_0004


def test_layer_budget() -> None:
    layers = tuple(
        MarkerLayer(markers=({"id": str(i), "lat": 0.0, "lon": 0.0, "label": str(i)},))
        for i in range(LIMITS["layers_per_map"] + 1)
    )
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                layers=layers,
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == HED_MAP_SPEC_0002


def test_feature_budget_reuses_core_limit() -> None:
    features = [
        {
            "type": "Feature",
            "properties": {"name": f"f{i}"},
            "geometry": {"type": "Point", "coordinates": [0.0, 0.0]},
        }
        for i in range(MAX_FEATURES + 1)
    ]
    with pytest.raises(HedronError) as exc:
        compile_map(
            MapSpec(
                layers=(GeoJSONLayer(data={"type": "FeatureCollection", "features": features}),),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )
    assert exc.value.diagnostic.code == "HED-MAP-0001"


def test_beginner_map_defaults_osm() -> None:
    html = Map(center=(37.77, -122.42), zoom=11, title="Bay", description="OSM").compile_plan()
    assert html.preset_id == "openstreetmap-standard"
    rendered = Map(center=(37.77, -122.42), zoom=11, title="Bay", description="OSM")
    from hedron_core import RenderMode, render

    out = render(rendered, mode=RenderMode.FRAGMENT).html
    assert "hedron-map" in out
    assert "data-hedron-payload" in out
    assert "hedron-map-alternative" in out


def test_missing_marker_coordinates_are_rejected() -> None:
    with pytest.raises(ValueError):
        compile_map(
            MapSpec(
                layers=(MarkerLayer(markers=({"id": "missing"},)),),
                accessibility=AccessibilityDef(title="T", description="D"),
            )
        )


def test_map_exposes_configured_csrf_names() -> None:
    from starlette.applications import Starlette
    from starlette.requests import Request

    from hedron.context import render_context_from_request
    from hedron_core import RenderMode, SecurityPolicy, render

    app = Starlette()
    app.state.hedron_security = SecurityPolicy(
        csrf_cookie_name="my_csrf", csrf_header_name="X-My-CSRF"
    )
    request = Request(
        {
            "type": "http",
            "app": app,
            "headers": [],
            "method": "GET",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "root_path": "",
            "scheme": "https",
            "server": ("testserver", 443),
            "client": ("127.0.0.1", 1234),
        }
    )

    out = render(
        Map(),
        context=render_context_from_request(request),
        mode=RenderMode.FRAGMENT,
    ).html
    assert 'data-hedron-csrf-cookie="my_csrf"' in out
    assert 'data-hedron-csrf-header="X-My-CSRF"' in out


def test_portable_modules_forbid_runtime_imports() -> None:
    forbidden = {"fastapi", "maplibre", "sqlite3", "httpx", "requests", "urllib.request", "socket"}
    for path in PORTABLE:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
                names.add(node.module)
        assert not (names & forbidden), path
