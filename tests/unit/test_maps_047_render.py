"""RENDER-047 host consumes MapPlan only."""

from __future__ import annotations

import json

from hedron_core import RenderMode, render
from hedron_maps import MAPLIBRE_VERSION, Map
from hedron_maps.assets_047 import map_module_path
from hedron_maps.element import TAG_NAME
from hedron_maps.pins import RUNTIME_PINS


def test_host_payload_is_mapplan() -> None:
    html = render(Map(title="Host", description="Plan only"), mode=RenderMode.FRAGMENT).html
    assert f"<{TAG_NAME}" in html or TAG_NAME in html
    assert "data-hedron-payload" in html
    # Attribute is HTML-escaped JSON; still contains schema_id.
    assert "hedron-map-spec/1" in html
    assert "maplibre" in html
    assert MAPLIBRE_VERSION in json.dumps(RUNTIME_PINS)


def test_host_module_lifecycle_and_wait_selector() -> None:
    src = map_module_path().read_text(encoding="utf-8")
    assert "data-hedron-map-mounted" in src
    assert "htmx:beforeSwap" in src
    assert "htmx:beforeCleanupElement" in src
    assert "AbortController" in src
    assert "cooperativeGestures" in src
    assert "prefers-reduced-motion" in src
    assert "hedron-chart" not in src
    assert "data-hedron-chart=" not in src
    assert RUNTIME_PINS["maplibre-csp"]["version"] == "5.6.1"
