"""Hedron-core feature explanation and route document contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

import pytest

from hedron_core.bundles import FeatureBundle, FeatureConflictError, FeatureRequirement
from hedron_core.catalog import PackageProjection
from hedron_core.feature_explanation import (
    EXPLANATION_SCHEMA,
    SOURCE_MAP_SCHEMA,
    FeatureExplanation,
    callable_ref,
    explain_feature,
    source_map_for,
)
from hedron_core.route_document import (
    EFFECT_GRAPH_SCHEMA,
    ROUTE_DOCUMENT_SCHEMA,
    export_effect_graph,
    export_routes_document,
)


@dataclass
class _Handle:
    logical_id: str
    path: str


def test_feature_explanation_uses_declared_projection_surfaces() -> None:
    bundle = FeatureBundle(
        logical_id="tests:declared",
        provider="tests",
        provider_version="1",
        views=(_Handle("ignored", "/ignored"),),
        projections=(
            PackageProjection(
                namespace="tests.feature.surfaces",
                data={
                    "surfaces": [
                        "summary",
                        {
                            "name": "editor",
                            "kind": "form",
                            "route": "/edit",
                            "handle_id": "edit-item",
                        },
                        "",
                        {"missing": "name"},
                    ]
                },
            ),
        ),
    )

    plan = explain_feature(bundle)

    assert plan["schema"] == EXPLANATION_SCHEMA
    assert plan["surfaces"] == [
        {"name": "summary", "kind": "declared"},
        {"name": "editor", "kind": "form", "route": "/edit", "handle_id": "edit-item"},
    ]
    assert plan["routes"] == [{"path": "/ignored", "logical_id": "ignored"}]


def test_feature_explanation_derives_handles_effects_security_and_source() -> None:
    view = _Handle("view-status", "/status")
    action = _Handle("action-save", "/save")
    object.__setattr__(action, "__hedron_effects__", ("refresh",))
    bundle = FeatureBundle(
        logical_id="tests:derived",
        provider="tests",
        provider_version="1.2.3",
        views=(view,),
        commands=(action, object()),
        requirements=(FeatureRequirement("database"), FeatureRequirement("gpu", required=False)),
        dependencies=("tests:base",),
        limitations=("offline-only",),
        optional_capabilities=("charts",),
        projections=(PackageProjection(namespace="tests.feature.meta"),),
    )

    plan = explain_feature(bundle)

    assert plan["kind"] == "FeatureBundle"
    assert plan["surfaces"][:2] == [
        {"name": "view-status", "kind": "view", "route": "/status", "handle_id": "view-status"},
        {
            "name": "action-save",
            "kind": "command",
            "route": "/save",
            "handle_id": "action-save",
        },
    ]
    assert plan["surfaces"][2] == {"name": "command", "kind": "command"}
    assert plan["effects"] == [{"handle": "action-save", "effects": "tuple"}]
    assert plan["security"] == {
        "requirements": [
            {"name": "database", "required": True, "kind": "package"},
            {"name": "gpu", "required": False, "kind": "package"},
        ],
        "optional_capabilities": ["charts"],
        "redacted": True,
    }
    assert plan["source"] == {
        "provider": "tests",
        "provider_version": "1.2.3",
        "dependencies": ["tests:base"],
        "projections": ["tests.feature.meta"],
    }


def test_feature_provider_name_and_mapping_round_trip() -> None:
    class ExampleProvider:
        def to_bundle(self) -> FeatureBundle:
            return FeatureBundle(
                logical_id="tests:provider", provider="tests", provider_version="1"
            )

    original = explain_feature(ExampleProvider())
    loaded = explain_feature(original)

    assert original["kind"] == "ExampleProvider"
    assert loaded == original
    assert FeatureExplanation("x", "bundle").to_mapping()["schema"] == EXPLANATION_SCHEMA


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ({"schema": "other/1"}, "Unsupported"),
        ({"routes": None}, "must be an array"),
        ({"security": []}, "must be an object"),
        ({"source": {1: "bad"}}, "non-string keys"),
        ({"limitations": [object()]}, "not JSON-compatible"),
    ],
)
def test_feature_plan_validation_fails_closed(mutation: dict[str, object], message: str) -> None:
    plan: dict[str, object] = {
        "schema": EXPLANATION_SCHEMA,
        "logical_id": "tests:plan",
        "kind": "FeatureBundle",
        "surfaces": [],
        "routes": [],
        "effects": [],
        "security": {},
        "limitations": [],
        "source": {},
    }
    plan.update(mutation)
    error_type = FeatureConflictError if "schema" in mutation else ValueError
    with pytest.raises(error_type, match=message):
        explain_feature(plan)


def test_feature_plan_requires_every_frozen_field() -> None:
    with pytest.raises(FeatureConflictError, match="Missing required field 'source'"):
        explain_feature(
            {
                "logical_id": "tests:plan",
                "kind": "bundle",
                "surfaces": [],
                "routes": [],
                "effects": [],
                "security": {},
                "limitations": [],
            }
        )


def test_callable_refs_never_invoke_values() -> None:
    calls: list[str] = []

    def callback() -> None:
        calls.append("called")

    class Metadata:
        pass

    class NamedCallable:
        __name__ = "named-callback"

        def __call__(self) -> None:
            calls.append("called")

    assert callable_ref(callback).endswith(".callback")
    assert callable_ref(Metadata).endswith(".Metadata")
    assert callable_ref(NamedCallable()) == "named-callback"
    assert callable_ref(None) is None
    assert callable_ref(1) is None
    assert calls == []


def test_feature_source_map_is_deterministic_and_sensitive_to_inputs() -> None:
    first = source_map_for(
        feature_id="tests:feature",
        selection="*",
        files=["feature.py", "source_map.json"],
        facade_source="source",
        catalog_payload={"b": 2, "a": 1},
        scenario_payload=["one"],
    )
    reordered = source_map_for(
        feature_id="tests:feature",
        selection="*",
        files=["feature.py", "source_map.json"],
        facade_source="source",
        catalog_payload={"a": 1, "b": 2},
        scenario_payload=["one"],
    )
    changed = source_map_for(
        feature_id="tests:feature",
        selection="*",
        files=[],
        facade_source="changed",
    )

    assert first == reordered
    assert first.facade_digest != changed.facade_digest
    assert first.to_mapping()["schema"] == SOURCE_MAP_SCHEMA


class _Mode(Enum):
    READ = "read"


@dataclass
class _Route:
    logical_id: str
    path: str
    endpoint: object
    metadata: object


class _RouteSource:
    def __init__(self, routes: list[object]) -> None:
        self._routes = routes

    def routes(self) -> list[object]:
        return self._routes


class _MappingValue:
    def as_mapping(self) -> object:
        return {"mode": _Mode.READ, "values": {3, 1, 2}}


def test_route_document_accepts_sources_and_normalizes_structured_values() -> None:
    calls: list[str] = []

    def endpoint() -> None:
        calls.append("called")

    route = _Route("b", "/b", endpoint, _MappingValue())
    source = _RouteSource([route, {"logical_id": "a", "path": "/a", "api-token": "secret"}])

    document = export_routes_document(source)

    assert document["schema"] == ROUTE_DOCUMENT_SCHEMA
    assert [item["logical_id"] for item in document["routes"]] == ["a", "b"]
    assert document["routes"][0]["api-token"] == "<redacted>"
    assert document["routes"][1]["metadata"] == {"mode": "read", "values": [1, 2, 3]}
    assert "endpoint" not in document["routes"][1]
    assert calls == []


def test_route_document_accepts_nested_mapping_generator_and_plain_object() -> None:
    class RouteObject:
        def __init__(self) -> None:
            self.logical_id = "object"
            self.path = "/object"
            self._private = "hidden"

    nested = export_routes_document({"routes": ({"logical_id": "nested"},)})
    generated = export_routes_document(item for item in ({"logical_id": "generated"},))
    object_doc = export_routes_document(RouteObject())

    assert nested["routes"][0]["logical_id"] == "nested"
    assert generated["routes"][0]["logical_id"] == "generated"
    assert object_doc["routes"] == [{"logical_id": "object", "path": "/object"}]


def test_route_document_rejects_non_mapping_values() -> None:
    with pytest.raises(TypeError, match="mapping-like routes"):
        export_routes_document(42)


class _EffectEntry:
    def __init__(self, logical_id: str) -> None:
        self.logical_id = logical_id

    def as_mapping(self) -> object:
        return {
            "logical_id": self.logical_id,
            "effect_state": _Mode.READ,
            "declared_target_ids": ("main",),
            "outcome_variant_ids": ["ok"],
        }


def test_effect_graph_accepts_catalog_nodes_and_mapping_sources() -> None:
    class Catalog:
        entries: ClassVar[dict[str, _EffectEntry]] = {
            "b": _EffectEntry("b"),
            "a": _EffectEntry("a"),
        }

    graph = export_effect_graph(Catalog())

    assert graph["schema"] == EFFECT_GRAPH_SCHEMA
    assert [node["logical_id"] for node in graph["nodes"]] == ["a", "b"]
    assert graph["nodes"][0]["effect_state"] == "read"
    assert graph["edges"] == [
        {"from": "a", "to": "ok", "kind": "outcome"},
        {"from": "a", "to": "main", "kind": "target"},
        {"from": "b", "to": "ok", "kind": "outcome"},
        {"from": "b", "to": "main", "kind": "target"},
    ]


def test_effect_graph_supports_nodes_key_and_ignores_blank_ids_and_scalar_edges() -> None:
    graph = export_effect_graph(
        {
            "nodes": [
                {"id": "kept", "declared_target_ids": "not-a-sequence"},
                {"id": "", "outcome_variant_ids": ["ignored"]},
            ]
        }
    )
    assert graph["nodes"] == [{"declared_target_ids": "not-a-sequence", "id": "kept"}]
    assert graph["edges"] == []


def test_effect_graph_rejects_invalid_mapping_source_and_primitives() -> None:
    class Invalid:
        def as_mapping(self) -> object:
            return []

    with pytest.raises(TypeError, match="must return a mapping"):
        export_effect_graph([Invalid()])
    with pytest.raises(TypeError, match="catalog-like entries"):
        export_effect_graph([object()])
