"""Read-only Explorer catalog, graph, and registry queries."""

from __future__ import annotations

from typing import Any, TypeVar

from fastapi import Request

from hedron_core.a11y import AccessibilityContract
from hedron_core.catalog import InteractionCatalog, compile_interaction_catalog, get_sealed_catalog
from hedron_core.dashboard import dashboard_graph_payload
from hedron_core.registry import ComponentMeta, RouteMeta, get_registry
from hedron_explorer.services.query import (
    A11Y_LIMIT,
    AUDIT_LIMIT,
    COMPONENTS_LIMIT,
    DEFAULT_LIMIT,
    Page,
    envelope,
    paginate,
    parse_cursor,
    parse_limit,
    search_filter,
    wants_envelope,
)
from hedron_explorer.services.runtime import AUDIT, redact

T = TypeVar("T")


def app_catalog(app: object) -> InteractionCatalog:
    cached = getattr(getattr(app, "state", None), "hedron_interactions", None)
    if isinstance(cached, InteractionCatalog):
        return cached
    live = get_sealed_catalog()
    if live is not None:
        return live
    return compile_interaction_catalog()


def find_component(name: str) -> ComponentMeta | None:
    """Resolve a registered component by exact logical id, short name, or suffix."""
    for component in get_registry().components():
        if (
            component.logical_id == name
            or component.name == name
            or component.logical_id.endswith(f".{name}")
        ):
            return component
    return None


def _page_or_all(items: list[T], request: Request | None, *, default: int, cap: int) -> Page[T]:
    if request is None:
        return paginate(items, offset=0, limit=max(len(items), 1))
    return paginate(
        items,
        offset=parse_cursor(request),
        limit=parse_limit(request, default=default, cap=cap),
    )


def _sort_items(items: list[T], request: Request | None, allowed: tuple[str, ...]) -> list[T]:
    if request is None:
        return items
    raw = request.query_params.get("sort")
    if not raw:
        return items
    reverse = raw.startswith("-")
    field = raw[1:] if reverse else raw
    if field not in allowed:
        return items
    return sorted(items, key=lambda item: str(getattr(item, field, "")).lower(), reverse=reverse)


def list_components(request: Request | None = None) -> list[ComponentMeta]:
    items = list(get_registry().components())
    query = None if request is None else request.query_params.get("q")

    def _component_haystack(component: ComponentMeta) -> str:
        return f"{component.name} {component.logical_id} {component.distribution}"

    filtered = search_filter(items, query, key=_component_haystack)
    return _sort_items(filtered, request, ("name", "logical_id", "distribution"))


def page_components(request: Request | None = None) -> Page[ComponentMeta]:
    items = list_components(request)
    return _page_or_all(items, request, default=COMPONENTS_LIMIT, cap=COMPONENTS_LIMIT)


def list_routes(request: Request | None = None) -> list[RouteMeta]:
    items = list(get_registry().routes())
    query = None if request is None else request.query_params.get("q")
    filtered = search_filter(items, query, key=lambda r: f"{r.kind} {r.name} {r.path}")
    return _sort_items(filtered, request, ("kind", "name", "path"))


def page_routes(request: Request | None = None) -> Page[RouteMeta]:
    items = list_routes(request)
    return _page_or_all(items, request, default=DEFAULT_LIMIT, cap=COMPONENTS_LIMIT)


def component_payload(c: ComponentMeta) -> dict[str, Any]:
    return {
        "name": c.name,
        "logical_id": c.logical_id,
        "distribution": c.distribution,
        "styles_path": redact(c.styles_path),
        "style_symbols": dict(c.style_symbols),
    }


def route_payload(r: RouteMeta) -> dict[str, Any]:
    return {
        "kind": r.kind,
        "name": r.name,
        "path": r.path,
        "methods": list(r.methods),
        "operation_id": r.operation_id,
        "htmx_inference": dict(r.htmx_inference),
        "explanations": [
            f"HX target inference: {dict(r.htmx_inference)}",
            "Override via explicit hx-* attributes on the component.",
        ],
    }


def components_json(request: Request | None = None) -> Any:
    page = page_components(request)
    items = [component_payload(c) for c in page.items]
    if wants_envelope(request, page):
        wrapped = envelope(page)
        wrapped["items"] = items
        return wrapped
    return items


def routes_json(request: Request | None = None) -> Any:
    page = page_routes(request)
    items = [route_payload(r) for r in page.items]
    if wants_envelope(request, page):
        wrapped = envelope(page)
        wrapped["items"] = items
        return wrapped
    return items


def graph_json(request: Request | None = None) -> dict[str, Any]:
    """Explorer asset graph. CLI adds inverse_consumers; this payload does not."""
    nodes = [{"id": c.logical_id, "name": c.name} for c in get_registry().components()]
    query = None if request is None else request.query_params.get("q")
    nodes = search_filter(nodes, query, key=lambda n: f"{n['id']} {n['name']}")
    page = _page_or_all(nodes, request, default=COMPONENTS_LIMIT, cap=COMPONENTS_LIMIT)
    kept = {str(item["id"]) for item in page.items if isinstance(item, dict)}
    edges = []
    for c in get_registry().components():
        if c.logical_id not in kept:
            continue
        if c.styles_path:
            edges.append(
                {
                    "from": c.logical_id,
                    "to": redact(c.styles_path),
                    "kind": "styles",
                }
            )
        for dep in c.browser_modules:
            edges.append(
                {
                    "from": c.logical_id,
                    "to": redact(dep),
                    "kind": "browser_module",
                }
            )
    return {
        "nodes": page.items,
        "edges": edges,
        "truncated": page.truncated,
        "total": page.total,
        "limit": page.limit,
        "offset": page.offset,
        "next_cursor": page.next_cursor,
        "diagnostic": page.diagnostic,
        "divergence": {
            "cli_only": ["inverse_consumers"],
            "note": "hedron graph CLI includes inverse_consumers; browser_module edges are shared",
        },
    }


def page_interactions(request: Request, catalog: InteractionCatalog) -> Page[Any]:
    items = list(catalog.entries.values())
    query = request.query_params.get("q")
    filtered = search_filter(items, query, key=lambda entry: f"{entry.logical_id} {entry.kind}")
    return paginate(
        filtered,
        offset=parse_cursor(request),
        limit=parse_limit(request, default=DEFAULT_LIMIT, cap=COMPONENTS_LIMIT),
    )


def handle_graph_json(request: Request) -> dict[str, Any]:
    from hedron_core.updates import handle_graph_payload, redacted_descriptor_view

    app_id = str(getattr(getattr(request.app, "state", None), "hedron_app_id", "") or "")
    payload = handle_graph_payload(app_id=app_id or None)
    handles = getattr(getattr(request.app, "state", None), "hedron_handles", {}) or {}
    redacted = []
    for handle in handles.values() if isinstance(handles, dict) else []:
        descriptor = getattr(handle, "descriptor", None)
        if descriptor is not None:
            redacted.append(redacted_descriptor_view(descriptor))
    return {**payload, "handles": redacted}


def interactions_json(request: Request) -> dict[str, Any]:
    catalog = app_catalog(request.app)
    return catalog.to_manifest(profile="development").as_mapping()


def dashboard_graph_json() -> dict[str, Any]:
    from hedron_core import InteractionGraph

    payload = dashboard_graph_payload(InteractionGraph())
    return {**payload, "stability": "experimental"}


def security_json(request: Request | None = None) -> dict[str, Any]:
    page = paginate(
        list(AUDIT),
        offset=parse_cursor(request),
        limit=parse_limit(request, default=AUDIT_LIMIT, cap=AUDIT_LIMIT),
    )
    payload: dict[str, Any] = {
        "findings": [
            "Explorer routes absent in production by default",
            "CSRF required for unsafe cookie-authenticated actions",
            "Authenticated fragments use private, no-store caching",
            "Mutation simulation disabled by default",
        ],
        "redacted": True,
        "audit_tail": page.items,
        "truncated": page.truncated,
        "total": page.total,
        "diagnostic": page.diagnostic,
    }
    return payload


def a11y_contracts(*, request: Request | None = None) -> Page[AccessibilityContract]:
    from hedron_core.a11y import AccessibilityContractCatalog, seed_reviewed_contracts

    catalog = AccessibilityContractCatalog()
    seed_reviewed_contracts(catalog)
    catalog.ensure_registry()
    all_contracts = list(catalog.contracts.values())
    ordered = sorted(all_contracts, key=lambda c: (not c.reviewed, c.component))
    query = None if request is None else request.query_params.get("q")
    filtered = search_filter(ordered, query, key=lambda c: c.component)
    return paginate(
        filtered,
        offset=parse_cursor(request),
        limit=parse_limit(request, default=A11Y_LIMIT, cap=A11Y_LIMIT),
    )


_app_catalog = app_catalog
_find_component = find_component
