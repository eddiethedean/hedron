"""Versioned route and effect document export (ROUTE-053 / RFC-0080).

Builders are framework-neutral: they consume route mappings or registry-like
objects and never import or call route handlers. Nested dict/list metadata is
preserved as typed JSON values (never silently stringified).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import is_dataclass
from enum import Enum
from typing import Protocol, TypeGuard, cast, runtime_checkable

__all__ = [
    "EFFECT_GRAPH_SCHEMA",
    "ROUTE_DOCUMENT_SCHEMA",
    "export_effect_graph",
    "export_routes_document",
]

ROUTE_DOCUMENT_SCHEMA = "hedron-route-document-1"
EFFECT_GRAPH_SCHEMA = "hedron-effect-graph-1"

_REDACT_TOKENS = frozenset({"secret", "password", "token", "cookie"})
_REDACTED = "<redacted>"
_SKIP_ROUTE_KEYS = frozenset({"endpoint", "handler", "callable", "fn", "func"})


def _is_object_sequence(value: object) -> TypeGuard[Sequence[object]]:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray))


@runtime_checkable
class _RouteSource(Protocol):
    def routes(self) -> Iterable[object]: ...


@runtime_checkable
class _MappingSource(Protocol):
    def as_mapping(self) -> object: ...


def _dataclass_mapping(value: object) -> dict[object, object]:
    raw_fields: object = getattr(value, "__dataclass_fields__", {})
    if not isinstance(raw_fields, Mapping):
        return {}
    field_names = cast(Mapping[object, object], raw_fields)
    return {
        name: getattr(value, name)
        for name in field_names
        if isinstance(name, str) and name not in _SKIP_ROUTE_KEYS
    }


def _is_redact_key(key: str) -> bool:
    lowered = str(key).lower().replace("-", "_")
    if lowered in _REDACT_TOKENS:
        return True
    return any(part in _REDACT_TOKENS for part in lowered.split("_") if part)


def _normalize_value(value: object) -> object:
    """Preserve nested mappings/lists; never stringify structured metadata."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Enum):
        return cast(object, value.value)
    if isinstance(value, Mapping):
        return _normalize_mapping(cast(Mapping[object, object], value))
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in cast(Iterable[object], value)]
    if isinstance(value, (set, frozenset)):
        items = [_normalize_value(item) for item in cast(Iterable[object], value)]
        return sorted(items, key=lambda item: repr(item))
    if callable(value):
        # Never invoke handlers; omit callables from the document.
        return None
    if is_dataclass(value) and not isinstance(value, type):
        return _normalize_mapping(_dataclass_mapping(value))
    if isinstance(value, _MappingSource):
        mapped = value.as_mapping()
        if isinstance(mapped, Mapping):
            return _normalize_mapping(cast(Mapping[object, object], mapped))
    return value


def _normalize_mapping(data: Mapping[object, object]) -> dict[str, object]:
    out: dict[str, object] = {}
    for raw_key, raw_value in data.items():
        key = str(raw_key)
        if key in _SKIP_ROUTE_KEYS:
            continue
        if _is_redact_key(key):
            out[key] = _REDACTED
            continue
        normalized = _normalize_value(raw_value)
        if normalized is None and callable(raw_value):
            continue
        out[key] = normalized
    return {key: out[key] for key in sorted(out)}


def _iter_routes(routes: object) -> list[Mapping[object, object]]:
    items: list[object]
    if isinstance(routes, Mapping):
        mapping = cast(Mapping[object, object], routes)
        nested = mapping.get("routes")
        items = list(nested) if _is_object_sequence(nested) else [mapping]
    elif _is_object_sequence(routes):
        items = list(routes)
    elif isinstance(routes, _RouteSource):
        items = list(routes.routes())
    elif isinstance(routes, Iterable) and not isinstance(routes, (str, bytes, bytearray)):
        items = list(cast(Iterable[object], routes))
    else:
        items = [routes]

    out: list[Mapping[object, object]] = []
    for item in items:
        if isinstance(item, Mapping):
            out.append(cast(Mapping[object, object], item))
        elif is_dataclass(item) and not isinstance(item, type):
            out.append(_dataclass_mapping(item))
        elif hasattr(item, "__dict__"):
            attributes = cast(Mapping[str, object], vars(item))
            out.append(
                {
                    key: value
                    for key, value in attributes.items()
                    if not key.startswith("_") and key not in _SKIP_ROUTE_KEYS
                }
            )
        else:
            raise TypeError(
                f"export_routes_document expected mapping-like routes, got {type(item)!r}"
            )
    return out


def _route_sort_key(route: Mapping[str, object]) -> tuple[str, str, str]:
    return (
        str(route.get("logical_id") or ""),
        str(route.get("path") or ""),
        str(route.get("name") or ""),
    )


def export_routes_document(routes: object) -> dict[str, object]:
    """Build a versioned, deterministic, redacted route document.

    Nested dict/list metadata is preserved as typed values. Callables such as
    ``endpoint`` / handlers are omitted and never invoked.
    """
    normalized = [_normalize_mapping(item) for item in _iter_routes(routes)]
    normalized.sort(key=_route_sort_key)
    return {
        "schema": ROUTE_DOCUMENT_SCHEMA,
        "routes": normalized,
    }


def _iter_entries(entries: object) -> list[Mapping[object, object]]:
    items: list[object]
    if isinstance(entries, Mapping):
        mapping = cast(Mapping[object, object], entries)
        nested_entries = mapping.get("entries")
        nested_nodes = mapping.get("nodes")
        if _is_object_sequence(nested_entries):
            items = list(nested_entries)
        elif _is_object_sequence(nested_nodes):
            items = list(nested_nodes)
        else:
            items = [mapping]
    elif _is_object_sequence(entries):
        items = list(entries)
    else:
        entries_map: object = getattr(entries, "entries", None)
        if isinstance(entries_map, Mapping):
            mapping = cast(Mapping[object, object], entries_map)
            items = list(mapping.values())
        elif isinstance(entries, Iterable) and not isinstance(entries, (str, bytes, bytearray)):
            items = list(cast(Iterable[object], entries))
        else:
            items = [entries]

    out: list[Mapping[object, object]] = []
    for item in items:
        if isinstance(item, Mapping):
            out.append(cast(Mapping[object, object], item))
        elif isinstance(item, _MappingSource):
            mapped = item.as_mapping()
            if not isinstance(mapped, Mapping):
                raise TypeError(f"entry.as_mapping() must return a mapping, got {type(mapped)!r}")
            out.append(cast(Mapping[object, object], mapped))
        else:
            if is_dataclass(item) and not isinstance(item, type):
                out.append(_dataclass_mapping(item))
            else:
                raise TypeError(
                    f"export_effect_graph expected catalog-like entries, got {type(item)!r}"
                )
    return out


def export_effect_graph(entries: object) -> dict[str, object]:
    """Export a deterministic effect graph from catalog-like entries.

    Each entry contributes a node keyed by ``logical_id`` (or ``id``) with its
    ``effect_state``. Declared target / outcome ids become typed edges.
    """
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, object]] = []
    for raw in _iter_entries(entries):
        node = _normalize_mapping(raw)
        node_id = str(node.get("logical_id") or node.get("id") or "")
        if not node_id:
            continue
        if "effect_state" not in node and "effect_state" in raw:
            node["effect_state"] = _normalize_value(raw["effect_state"])
            node = {key: node[key] for key in sorted(node)}
        nodes.append(node)
        targets = raw.get("declared_target_ids")
        for target in _object_items(targets):
            edges.append(
                {
                    "from": node_id,
                    "to": str(target),
                    "kind": "target",
                }
            )
        outcomes = raw.get("outcome_variant_ids")
        for outcome in _object_items(outcomes):
            edges.append(
                {
                    "from": node_id,
                    "to": str(outcome),
                    "kind": "outcome",
                }
            )
    nodes.sort(key=lambda item: str(item.get("logical_id") or item.get("id") or ""))
    edges.sort(key=lambda item: (str(item["from"]), str(item["kind"]), str(item["to"])))
    return {
        "schema": EFFECT_GRAPH_SCHEMA,
        "edges": edges,
        "nodes": nodes,
    }


def _object_items(value: object) -> Sequence[object]:
    return value if _is_object_sequence(value) else ()
