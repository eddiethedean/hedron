"""ROUTE-053 evidence."""

from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path

from hedron_core import (
    EFFECT_GRAPH_SCHEMA,
    ROUTE_DOCUMENT_SCHEMA,
    export_effect_graph,
    export_routes_document,
)
from hedron_core.route_document import ROUTE_DOCUMENT_SCHEMA as SCHEMA_DIRECT


def test_route_053_packet_bound() -> None:
    gate = tomllib.loads(Path("docs/acceptance/release-gate-0.53.toml").read_text(encoding="utf-8"))
    rows = {row["id"]: row for row in gate["evidence"]}
    assert rows["ROUTE-053"]["state"] == "Verified"
    assert Path("docs/rfcs/RFC-0080-APPLICATION-DX-CONTRACTS.md").is_file()


def test_route_document_schema_constant() -> None:
    assert ROUTE_DOCUMENT_SCHEMA == "hedron-route-document-1"
    assert SCHEMA_DIRECT == ROUTE_DOCUMENT_SCHEMA
    assert EFFECT_GRAPH_SCHEMA == "hedron-effect-graph-1"


def test_export_routes_document_typed_nested_and_deterministic() -> None:
    routes = [
        {
            "name": "beta",
            "path": "/b",
            "logical_id": "b",
            "htmx_inference": {
                "fragment_regions": [
                    {"id": "toast", "role": "status"},
                    {"id": "main", "role": "main"},
                ],
                "zx_meta": {"nested": True, "count": 2},
            },
            "password": "should-not-leak",
            "api_token": "tok",
            "Cookie": "session=1",
            "SECRET": "x",
        },
        {
            "name": "alpha",
            "path": "/a",
            "logical_id": "a",
            "methods": ("GET", "POST"),
            "metadata": {"tags": ["x", "y"], "limits": {"max": 3}},
        },
    ]
    doc = export_routes_document(routes)
    assert doc["schema"] == ROUTE_DOCUMENT_SCHEMA
    assert list(doc.keys()) == ["schema", "routes"]
    assert [r["logical_id"] for r in doc["routes"]] == ["a", "b"]
    alpha, beta = doc["routes"]
    assert list(alpha.keys()) == sorted(alpha.keys())
    assert isinstance(alpha["metadata"]["tags"], list)
    assert alpha["metadata"]["tags"] == ["x", "y"]
    assert isinstance(alpha["metadata"]["limits"], dict)
    assert alpha["metadata"]["limits"]["max"] == 3
    assert isinstance(beta["htmx_inference"]["fragment_regions"], list)
    assert beta["htmx_inference"]["fragment_regions"][0]["id"] == "toast"
    assert beta["password"] == "<redacted>"
    assert beta["api_token"] == "<redacted>"
    assert beta["Cookie"] == "<redacted>"
    assert beta["SECRET"] == "<redacted>"
    # Deterministic JSON dump (sorted keys already applied).
    encoded = json.dumps(doc, sort_keys=True)
    assert encoded == json.dumps(export_routes_document(list(reversed(routes))), sort_keys=True)


def test_export_routes_document_never_calls_handlers() -> None:
    calls: list[str] = []

    def handler() -> str:
        calls.append("called")
        return "nope"

    @dataclass
    class FakeRoute:
        kind: str
        logical_id: str
        name: str
        path: str
        endpoint: object
        htmx_inference: dict

    route = FakeRoute(
        kind="page",
        logical_id="home",
        name="home",
        path="/",
        endpoint=handler,
        htmx_inference={"fragment_regions": [{"id": "main"}]},
    )
    doc = export_routes_document([route])
    assert calls == []
    assert "endpoint" not in doc["routes"][0]
    assert doc["routes"][0]["htmx_inference"]["fragment_regions"][0]["id"] == "main"


def test_export_effect_graph_from_catalog_like_entries() -> None:
    entries = [
        {
            "logical_id": "cmd.refresh",
            "effect_state": "declared",
            "declared_target_ids": ["region.main", "region.toast"],
            "token": "hide-me",
        },
        {
            "logical_id": "view.home",
            "effect_state": "observed",
            "outcome_variant_ids": ["ok", "err"],
        },
    ]
    graph = export_effect_graph(entries)
    assert graph["schema"] == EFFECT_GRAPH_SCHEMA
    assert [n["logical_id"] for n in graph["nodes"]] == ["cmd.refresh", "view.home"]
    assert graph["nodes"][0]["effect_state"] == "declared"
    assert graph["nodes"][0]["token"] == "<redacted>"
    kinds = {(e["from"], e["kind"], e["to"]) for e in graph["edges"]}
    assert ("cmd.refresh", "target", "region.main") in kinds
    assert ("view.home", "outcome", "ok") in kinds
