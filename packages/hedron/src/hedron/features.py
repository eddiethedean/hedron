"""Flagship FastAPI FeatureBundle inclusion (phase 0.46)."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from hedron_core.bundles import (
    FeatureBundle,
    FeatureConflictError,
    FeatureProvider,
    eject_bundle,
    eject_source,
    include_bundle,
    included_bundles,
    resolve_feature,
)
from hedron_core.codes import HED_BUNDLE_0006
from hedron_core.diagnostics import DiagnosticSeverity, make_diagnostic
from hedron_core.updates import list_handle_descriptors, unregister_handle_descriptor

__all__ = [
    "include_feature",
    "materialize_feature",
    "rollback_materialized",
]


def _is_handle(item: object) -> bool:
    return hasattr(item, "logical_id") and hasattr(item, "descriptor")


def _materialize_item(item: object, app: object) -> object:
    if _is_handle(item):
        return item
    if callable(item) and not isinstance(item, type):
        return item(app)
    return item


def _host_routers(app: object) -> list[object]:
    routers: list[object] = []
    root = getattr(app, "_root_router", None)
    if root is not None:
        routers.append(root)
    fastapi_router = getattr(app, "router", None)
    if fastapi_router is not None and fastapi_router is not root:
        routers.append(fastapi_router)
    return routers


def _collect_new_routes(app: object, snapshot: Sequence[object]) -> list[object]:
    found: list[object] = []
    seen: set[int] = set()
    for router in _host_routers(app):
        for route in list(getattr(router, "routes", [])):
            if route in snapshot or id(route) in seen:
                continue
            seen.add(id(route))
            found.append(route)
    return found


def _drop_routes(app: object, routes: Sequence[object]) -> None:
    for router in _host_routers(app):
        live_routes = getattr(router, "routes", None)
        if not isinstance(live_routes, list):
            continue
        for route in routes:
            if route in live_routes:
                with _suppress():
                    live_routes.remove(route)


def _record_bundle_routes(app: object, logical_id: str, routes: Sequence[object]) -> None:
    state = getattr(app, "state", None)
    if state is None:
        return
    recorded = getattr(state, "hedron_bundle_routes", None)
    if not isinstance(recorded, dict):
        state.hedron_bundle_routes = {}
        recorded = state.hedron_bundle_routes
    recorded[logical_id] = list(routes)


def rollback_materialized(
    items: list[object],
    *,
    app: object,
    routes_snapshot: list[object] | None = None,
    keep_logical_ids: set[str] | None = None,
) -> None:
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    state = getattr(app, "state", None)
    handles = getattr(state, "hedron_handles", None)
    preserved = keep_logical_ids or set()
    if routes_snapshot is not None:
        _drop_routes(app, _collect_new_routes(app, routes_snapshot))
    for item in items:
        ident = getattr(item, "logical_id", None)
        if not isinstance(ident, str) or ident in preserved:
            continue
        unregister_handle_descriptor(ident, app_id=app_id)
        if isinstance(handles, dict):
            handles.pop(ident, None)


class _suppress:
    def __enter__(self) -> None:
        return None

    def __exit__(self, *exc: object) -> bool:
        return True


def materialize_feature(bundle: FeatureBundle, app: object) -> FeatureBundle:
    views = tuple(_materialize_item(item, app) for item in bundle.views)
    commands = tuple(_materialize_item(item, app) for item in bundle.commands)
    return FeatureBundle(
        logical_id=bundle.logical_id,
        provider=bundle.provider,
        provider_version=bundle.provider_version,
        views=views,
        commands=commands,
        components=bundle.components,
        scenarios=bundle.scenarios,
        projections=bundle.projections,
        requirements=bundle.requirements,
        dependencies=bundle.dependencies,
        limitations=bundle.limitations,
        optional_capabilities=bundle.optional_capabilities,
    )


def include_feature(
    app: object,
    feature: FeatureBundle | FeatureProvider,
    *,
    capabilities: Mapping[str, bool] | None = None,
) -> FeatureBundle:
    """Include one validated bundle before registry/catalog seal.

    Accepts a ``FeatureBundle`` or a ``FeatureProvider`` (``to_bundle()``).
    A ``DataWorkspace`` is a provider; beginner spelling is
    ``app.include_feature(orders)``.
    """
    from hedron_core.catalog import get_sealed_catalog

    if get_sealed_catalog() is not None:
        from hedron_core.bundles import FeatureConflictError as Conflict
        from hedron_core.codes import HED_BUNDLE_0001

        raise Conflict(
            make_diagnostic(
                HED_BUNDLE_0001,
                severity=DiagnosticSeverity.ERROR,
                title="Cannot include FeatureBundle after catalog seal",
                explanation="include_feature must run in the same window as include_component.",
                remediation="Register bundles during app construction or plugin start.",
            )
        )
    resolved = resolve_feature(feature)
    router = getattr(app, "_root_router", None)
    snapshot_routes = list(getattr(router, "routes", [])) if router is not None else []
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    prior_ids = {item.logical_id for item in list_handle_descriptors(app_id=app_id)}
    known: list[str] = []
    for item in included_bundles(app_id=app_id):
        for handle in (*item.views, *item.commands):
            ident = getattr(handle, "logical_id", None)
            if isinstance(ident, str) and ident:
                known.append(ident)
    materialized_items: list[object] = []
    try:
        live = materialize_feature(resolved, app)
        materialized_items.extend((*live.views, *live.commands))
        caps = dict(capabilities or {})
        caps.setdefault(live.provider, True)
        include_bundle(
            live,
            app_id=app_id,
            capabilities=caps,
            known_logical_ids=known,
        )
        state = getattr(app, "state", None)
        if state is not None:
            recorded = getattr(state, "hedron_bundles", None)
            if not isinstance(recorded, dict):
                state.hedron_bundles = {}
                recorded = state.hedron_bundles
            recorded[live.logical_id] = live
        _record_bundle_routes(app, live.logical_id, _collect_new_routes(app, snapshot_routes))
        return live
    except FeatureConflictError:
        rollback_materialized(
            materialized_items,
            app=app,
            routes_snapshot=snapshot_routes,
            keep_logical_ids=prior_ids,
        )
        raise
    except Exception as exc:
        rollback_materialized(
            materialized_items,
            app=app,
            routes_snapshot=snapshot_routes,
            keep_logical_ids=prior_ids,
        )
        raise FeatureConflictError(
            make_diagnostic(
                HED_BUNDLE_0006,
                severity=DiagnosticSeverity.ERROR,
                title="FeatureBundle include rolled back",
                explanation=f"Including {resolved.logical_id!r} failed: {exc}",
                remediation="Fix the conflict and include again; no partial artifacts remain.",
            )
        ) from exc


def eject_feature(app: object, logical_id: str, *, out: Callable[[str], None] | None = None) -> str:
    app_id = str(getattr(app, "hedron_app_id", "") or "")
    bundle = eject_bundle(logical_id, app_id=app_id)
    source = eject_source(bundle)
    state = getattr(app, "state", None)
    recorded = getattr(state, "hedron_bundles", None)
    if isinstance(recorded, dict):
        recorded.pop(logical_id, None)
    routes_map = getattr(state, "hedron_bundle_routes", None)
    extra = routes_map.pop(logical_id, []) if isinstance(routes_map, dict) else []
    _drop_routes(app, extra)
    handles = getattr(state, "hedron_handles", None)
    if isinstance(handles, dict):
        for item in (*bundle.views, *bundle.commands):
            ident = getattr(item, "logical_id", None)
            if isinstance(ident, str):
                handles.pop(ident, None)
    if out is not None:
        out(source)
    return source
