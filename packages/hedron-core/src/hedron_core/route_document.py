"""Versioned route and effect document export (ROUTE-053 / RFC-0080).

Builders are framework-neutral: they consume route mappings or registry-like
objects and never import or call route handlers. Nested dict/list metadata is
preserved as typed JSON values (never silently stringified).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import fields, is_dataclass
from enum import Enum
from typing import Any

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
        return value.value
    if isinstance(value, Mapping):
        return _normalize_mapping(value)
    if isinstance(value, (list, tuple)):
        return [_normalize_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [_normalize_value(item) for item in value]
        return sorted(items, key=lambda item: repr(item))
    if callable(value):
        # Never invoke handlers; omit callables from the document.
        return None
    if is_dataclass(value) and not isinstance(value, type):
        return _normalize_mapping(
            {
                f.name: getattr(value, f.name)
                for f in fields(value)
                if f.name not in _SKIP_ROUTE_KEYS
            }
        )
    if hasattr(value, "as_mapping") and callable(value.as_mapping):
        mapped = value.as_mapping()
        if isinstance(mapped, Mapping):
            return _normalize_mapping(mapped)
    return value


def _normalize_mapping(data: Mapping[Any, Any]) -> dict[str, object]:
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


def _iter_routes(routes: Sequence[Mapping[Any, Any]] | object) -> list[Mapping[Any, Any]]:
    if isinstance(routes, Mapping):
        if "routes" in routes and isinstance(routes["routes"], Sequence):
            items = list(routes["routes"])
        else:
            items = [routes]
    elif isinstance(routes, Sequence) and not isinstance(routes, (str, bytes, bytearray)):
        items = list(routes)
    elif hasattr(routes, "routes") and callable(routes.routes):
        items = list(routes.routes())
    elif isinstance(routes, Iterable) and not isinstance(routes, (str, bytes, bytearray)):
        items = list(routes)
    else:
        items = [routes]

    out: list[Mapping[Any, Any]] = []
    for item in items:
        if isinstance(item, Mapping):
            out.append(item)
        elif is_dataclass(item) and not isinstance(item, type):
            out.append(
                {
                    f.name: getattr(item, f.name)
                    for f in fields(item)
                    if f.name not in _SKIP_ROUTE_KEYS
                }
            )
        elif hasattr(item, "__dict__"):
            out.append(
                {
                    key: value
                    for key, value in vars(item).items()
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


def export_routes_document(routes: Sequence[Mapping[Any, Any]] | object) -> dict[str, object]:
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


def _iter_entries(entries: object) -> list[Mapping[Any, Any]]:
    if isinstance(entries, Mapping):
        if "entries" in entries and isinstance(entries["entries"], Sequence):
            items = list(entries["entries"])
        elif "nodes" in entries and isinstance(entries["nodes"], Sequence):
            items = list(entries["nodes"])
        else:
            items = [entries]
    elif isinstance(entries, Sequence) and not isinstance(entries, (str, bytes, bytearray)):
        items = list(entries)
    elif hasattr(entries, "entries") and isinstance(getattr(entries, "entries"), Mapping):
        items = list(entries.entries.values())
    elif isinstance(entries, Iterable) and not isinstance(entries, (str, bytes, bytearray)):
        items = list(entries)
    else:
        items = [entries]

    out: list[Mapping[Any, Any]] = []
    for item in items:
        if isinstance(item, Mapping):
            out.append(item)
        elif hasattr(item, "as_mapping") and callable(item.as_mapping):
            mapped = item.as_mapping()
            if isinstance(mapped, Mapping):
                out.append(mapped)
            else:
                raise TypeError(f"entry.as_mapping() must return a mapping, got {type(mapped)!r}")
        elif is_dataclass(item) and not isinstance(item, type):
            out.append({f.name: getattr(item, f.name) for f in fields(item)})
        else:
            raise TypeError(f"export_effect_graph expected catalog-like entries, got {type(item)!r}")
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
        for target in list(raw.get("declared_target_ids") or ()):
            edges.append(
                {
                    "from": node_id,
                    "to": str(target),
                    "kind": "target",
                }
            )
        for outcome in list(raw.get("outcome_variant_ids") or ()):
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
