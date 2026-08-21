"""HedronRouter with page, component, and action registration."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Sequence
from contextvars import ContextVar
from enum import Enum
from typing import Any, ParamSpec, TypeVar

from fastapi import params
from fastapi.routing import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from hedron.async_utils import await_if_needed
from hedron.openapi import operation_id_for
from hedron.routing.route import HedronRoute
from hedron.security.csrf import prepare_csrf_from_request, validate_csrf
from hedron.security.policy import SecurityPolicy
from hedron_core.addressable import AddressableDescriptor
from hedron_core.identifiers import component_type_id
from hedron_core.interaction import FragmentRegion
from hedron_core.registry import register_route
from hedron_core.rendering import RenderMode

P = ParamSpec("P")
R = TypeVar("R")

__all__ = ["HedronRouter", "current_request"]

current_request: ContextVar[Request | None] = ContextVar("hedron_current_request", default=None)

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _logical_id(fn: Callable[..., object], distribution: str = "hedron") -> str:
    module = getattr(fn, "__module__", None) or "hedron"
    name = getattr(fn, "__name__", None) or "endpoint"
    return component_type_id(distribution, module, name)


def _requires_csrf(methods: Sequence[str]) -> bool:
    return any(m.upper() not in _SAFE_METHODS for m in methods)


def _fragment_regions_for_inference(
    regions: Sequence[FragmentRegion],
) -> list[dict[str, str]]:
    """Typed nested metadata for route documents (ROUTE-053; never stringify)."""
    return [
        {
            "id": region.id,
            "selector": region.selector,
            "description": region.description,
        }
        for region in regions
    ]


def _normalize_fragment_regions(
    fragment_regions: Sequence[FragmentRegion | str] | FragmentRegion | str | None,
) -> tuple[FragmentRegion, ...]:
    if not fragment_regions:
        return ()
    if isinstance(fragment_regions, (FragmentRegion, str)):
        fragment_regions = (fragment_regions,)
    out: list[FragmentRegion] = []
    for r in fragment_regions:
        if isinstance(r, FragmentRegion):
            out.append(r)
            continue
        name = str(r).removeprefix("#")
        out.append(FragmentRegion(id=name, selector=f"#{name}"))
    return tuple(out)


def _wrap_endpoint(
    fn: Callable[..., object],
    *,
    kind: str,
    mode: RenderMode | None,
    require_csrf: bool,
    fragment_regions: tuple[FragmentRegion, ...] = (),
    allow_undeclared_targets: bool = False,
    capability: str | None = None,
    idempotency: str | None = None,
) -> Callable[..., Response]:
    import typing

    @functools.wraps(fn)
    async def endpoint(*args: Any, **kwargs: Any) -> Response:
        request = current_request.get()
        if request is None:
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            maybe = kwargs.get("request")
            if isinstance(maybe, Request):
                request = maybe
        if request is None:
            raise RuntimeError("Hedron endpoints require an active Request")
        if require_csrf and request.method.upper() not in _SAFE_METHODS:
            policy: SecurityPolicy = getattr(
                request.app.state, "hedron_security", SecurityPolicy.from_name("standard")
            )
            await prepare_csrf_from_request(request, policy)
            validate_csrf(request, policy)
        # CAP-055: enforce capability after CSRF, before side effects.
        if capability:
            from hedron.capabilities import enforce_capability

            enforce_capability(request, capability)
        replay_claim = None
        replay_policy = None
        replay_store = None
        replay_key = None
        replay_fp = None
        replay_scope_key = None
        if idempotency and idempotency != "off":
            from starlette.responses import Response as StarletteResponse

            from hedron.replay import (
                IdempotencyPolicy,
                ReplayState,
                digest_bytes,
                extract_idempotency_key,
                fingerprint_request,
                replay_scope,
                resolve_replay_store,
            )

            replay_policy = IdempotencyPolicy(mode=idempotency)  # type: ignore[arg-type]
            replay_key = await extract_idempotency_key(request, replay_policy)
            if replay_policy.mode == "required" and not replay_key:
                from hedron_core.diagnostics import error

                raise error(
                    "HED-REPLAY-0001",
                    title="Idempotency key required",
                    explanation="This action requires an Idempotency-Key.",
                    remediation="Send the Idempotency-Key header or form field.",
                )
            if replay_key:
                subject = str(
                    getattr(getattr(request, "user", None), "identity", "") or "anonymous"
                )
                tenant = str(getattr(request.state, "hedron_tenant", "") or "")
                session = str(
                    getattr(request.state, "session_id", None)
                    or request.cookies.get("session")
                    or request.cookies.get("hedron_session")
                    or ""
                )
                body_digest = ""
                try:
                    raw_body = await request.body()
                    body_digest = digest_bytes(raw_body or b"")
                except (RuntimeError, OSError, ValueError, TypeError):
                    body_digest = f"len:{request.headers.get('content-length', '')}"
                replay_fp = fingerprint_request(
                    action_id=getattr(fn, "__name__", "action"),
                    subject=subject,
                    tenant=tenant,
                    inputs={
                        "path": str(request.url.path),
                        "method": request.method,
                        "query": str(request.url.query),
                        "content_type": str(request.headers.get("content-type") or ""),
                        "body_sha256": body_digest,
                    },
                    policy_version=replay_policy.policy_version,
                )
                replay_store = resolve_replay_store(request)
                replay_scope_key = replay_scope(
                    tenant=tenant,
                    subject=subject,
                    action_id=getattr(fn, "__name__", "action"),
                    session=session,
                )
                replay_claim = replay_store.claim(
                    key=replay_key,
                    fingerprint=replay_fp,
                    scope=replay_scope_key,
                    retention_seconds=replay_policy.retention_seconds,
                )
                if replay_claim.state == ReplayState.CONFLICT:
                    from hedron_core.diagnostics import error

                    raise error(
                        "HED-REPLAY-0002",
                        title="Idempotency key conflict",
                        explanation="The key was reused with a different request fingerprint.",
                        remediation="Use a new key for distinct mutations.",
                    )
                if replay_claim.state == ReplayState.IN_FLIGHT:
                    from hedron_core.diagnostics import error

                    raise error(
                        "HED-REPLAY-0003",
                        title="Idempotency key in flight",
                        explanation="A concurrent request already claimed this key.",
                        remediation="Retry after the first request completes.",
                    )
                if replay_claim.state == ReplayState.REPLAYED:
                    return StarletteResponse(
                        content=replay_claim.cached_body or b"",
                        status_code=int(replay_claim.cached_status or 200),
                        media_type=replay_claim.cached_media_type or "text/html",
                        headers={"Hedron-Replay": "true"},
                    )
        try:
            result = fn(*args, **kwargs)
            result = await await_if_needed(result)
            response = await HedronRoute.convert_endpoint_result(
                request,
                result,  # type: ignore[arg-type]
                mode=mode,
                kind=kind,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
        except Exception:
            if (
                replay_claim is not None
                and replay_store is not None
                and replay_key is not None
                and replay_fp is not None
                and replay_scope_key is not None
            ):
                from hedron.replay import ReplayState

                if replay_claim.state == ReplayState.FIRST:
                    replay_store.abort(
                        key=replay_key, scope=replay_scope_key, fingerprint=replay_fp
                    )
            raise
        if (
            replay_claim is not None
            and replay_store is not None
            and replay_key is not None
            and replay_fp is not None
            and replay_scope_key is not None
        ):
            from hedron.replay import ReplayState

            if replay_claim.state == ReplayState.FIRST:
                body = getattr(response, "body", None)
                if body is None and hasattr(response, "render"):
                    # Materialize Starlette Response body when not yet sent.
                    try:
                        body = response.render(getattr(response, "content", b""))
                    except (AttributeError, TypeError, ValueError, RuntimeError):
                        body = b""
                if body is None:
                    body = b""
                if isinstance(body, memoryview):
                    body = body.tobytes()
                if isinstance(body, str):
                    body = body.encode("utf-8")
                media_type = getattr(response, "media_type", None) or "text/html"
                replay_store.complete(
                    key=replay_key,
                    scope=replay_scope_key,
                    fingerprint=replay_fp,
                    status=int(getattr(response, "status_code", 200) or 200),
                    body=bytes(body),
                    media_type=str(media_type),
                )
        return response

    # Resolve annotations in the original function's globals so Depends survives wrapping.
    try:
        hints = typing.get_type_hints(fn, include_extras=True)
    except (NameError, TypeError, AttributeError, RecursionError):
        # Nested locals / unresolved forward refs — FastAPI still gets a usable signature.
        hints = {}
    sig = inspect.signature(fn)
    params = [
        # Type-authoring may have installed a concrete FastAPI signature on the
        # function before it reaches the router.  Preserve those annotations;
        # replacing them with the original type hints silently turns native
        # query models back into request bodies.
        param.replace(annotation=hints[name])
        if isinstance(param.annotation, str) and name in hints
        else param
        for name, param in sig.parameters.items()
    ]
    endpoint.__signature__ = sig.replace(  # type: ignore[attr-defined]
        parameters=params,
        return_annotation=(
            hints.get("return", sig.return_annotation)
            if isinstance(sig.return_annotation, str)
            else sig.return_annotation
        ),
    )
    endpoint._hedron_fragment_regions = fragment_regions  # type: ignore[attr-defined]
    if capability:
        endpoint._hedron_capability = capability  # type: ignore[attr-defined]
    if idempotency:
        endpoint._hedron_idempotency = idempotency  # type: ignore[attr-defined]
    logical = getattr(fn, "_hedron_view_logical_id", None)
    if logical:
        endpoint._hedron_view_logical_id = logical  # type: ignore[attr-defined]
    return endpoint  # type: ignore[return-value]


class HedronRouter(APIRouter):
    """APIRouter with Hedron page/component/action decorators."""

    def __init__(self, *args: Any, provenance: str = "", **kwargs: Any) -> None:
        kwargs.setdefault("route_class", HedronRoute)
        super().__init__(*args, **kwargs)
        self.hedron_provenance = provenance or str(self.prefix or "")
        self._hedron_host_app: object | None = None

    def _fail_closed_late(self) -> None:
        from hedron.registration import fail_closed_late_registration
        from hedron_core.catalog import get_sealed_catalog
        from hedron_core.registry.builder import active_builder

        host = self._hedron_host_app
        fail_closed_late_registration(
            registry_sealed=active_builder()._sealed,
            catalog_sealed=get_sealed_catalog() is not None,
            openapi_cached=getattr(host, "openapi_schema", None) is not None,
        )

    def add_api_route(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        self._fail_closed_late()
        super().add_api_route(*args, **kwargs)
        if self.routes:
            self.routes[-1].hedron_provenance = self.hedron_provenance or self.prefix  # type: ignore[attr-defined]

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        self._fail_closed_late()
        if isinstance(router, HedronRouter) and self._hedron_host_app is not None:
            router._hedron_host_app = self._hedron_host_app
        super().include_router(router, *args, **kwargs)

    def _register_route_or_rollback(self, **kwargs: Any) -> None:
        try:
            register_route(**kwargs)
        except Exception:
            if self.routes:
                self.routes.pop()
            raise

    def page(
        self,
        path: str,
        *,
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            from hedron.responses import PageResponse

            route_name = name or fn.__name__
            logical_id = _logical_id(fn)
            verb_list = list(methods or ["GET"])
            op_id = operation_id_for("page", route_name, path, verb_list[0])
            regions = _normalize_fragment_regions(fragment_regions)
            fn._hedron_fragment_regions = regions  # type: ignore[attr-defined]
            wrapped = _wrap_endpoint(
                fn,
                kind="page",
                mode=None,
                require_csrf=_requires_csrf(verb_list),
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.add_api_route(
                path,
                wrapped,
                methods=verb_list,
                name=route_name,
                operation_id=op_id,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                tags=tags,
                response_class=kwargs.pop("response_class", None) or PageResponse,
                response_model=None,
                **kwargs,
            )
            self._register_route_or_rollback(
                kind="page",
                logical_id=logical_id,
                name=route_name,
                path=f"{self.prefix}{path}",
                methods=tuple(m.upper() for m in verb_list),
                operation_id=op_id,
                include_in_schema=include_in_schema,
                module=fn.__module__,
                tags=tuple(str(t) for t in (tags or ())),
                docs=inspect.getdoc(fn),
                endpoint=fn,
                htmx_inference={
                    "page_fragment": "HX-Request selects FRAGMENT vs PAGE",
                    "history": "browser history for full-page navigation",
                    "fragment_regions": _fragment_regions_for_inference(regions),
                    "boosted": "title/history/assets preserved; full-page fallback required",
                },
            )
            return fn

        return decorator

    def component(
        self,
        path: str,
        *,
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            from hedron.responses import FragmentResponse

            route_name = name or fn.__name__
            logical_id = _logical_id(fn)
            verb_list = list(methods or ["GET"])
            op_id = operation_id_for("component", route_name, path, verb_list[0])
            regions = _normalize_fragment_regions(fragment_regions)
            fn._hedron_fragment_regions = regions  # type: ignore[attr-defined]
            wrapped = _wrap_endpoint(
                fn,
                kind="component",
                mode=RenderMode.FRAGMENT,
                require_csrf=_requires_csrf(verb_list),
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.add_api_route(
                path,
                wrapped,
                methods=verb_list,
                name=route_name,
                operation_id=op_id,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                tags=tags,
                response_class=kwargs.pop("response_class", None) or FragmentResponse,
                response_model=None,
                **kwargs,
            )
            self._register_route_or_rollback(
                kind="component",
                logical_id=logical_id,
                name=route_name,
                path=f"{self.prefix}{path}",
                methods=tuple(m.upper() for m in verb_list),
                operation_id=op_id,
                include_in_schema=include_in_schema,
                module=fn.__module__,
                tags=tuple(str(t) for t in (tags or ())),
                docs=inspect.getdoc(fn),
                endpoint=fn,
                htmx_inference={
                    "default_mode": "fragment",
                    "target": "caller-provided hx-target",
                    "swap": "outerHTML",
                    "fragment_regions": _fragment_regions_for_inference(regions),
                    "csrf_required": str(_requires_csrf(verb_list)).lower(),
                },
            )
            return fn

        return decorator

    def action(
        self,
        path: str,
        *,
        method: str = "POST",
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        capability: str | None = None,
        idempotency: str | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        verb_list = list(methods or [method])

        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            from hedron.responses import FragmentResponse

            route_name = name or fn.__name__
            logical_id = _logical_id(fn)
            primary = verb_list[0].upper()
            op_id = operation_id_for("action", route_name, path, primary)
            regions = _normalize_fragment_regions(fragment_regions)
            fn._hedron_fragment_regions = regions  # type: ignore[attr-defined]
            if capability:
                fn._hedron_capability = capability  # type: ignore[attr-defined]
            if idempotency:
                fn._hedron_idempotency = idempotency  # type: ignore[attr-defined]
            wrapped = _wrap_endpoint(
                fn,
                kind="action",
                mode=RenderMode.FRAGMENT,
                require_csrf=_requires_csrf(verb_list),
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
                capability=capability,
                idempotency=idempotency,
            )
            self.add_api_route(
                path,
                wrapped,
                methods=verb_list,
                name=route_name,
                operation_id=op_id,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                tags=tags,
                response_class=kwargs.pop("response_class", None) or FragmentResponse,
                response_model=None,
                **kwargs,
            )
            route = self.routes[-1]
            if isinstance(route, HedronRoute):
                route.hedron_kind = "action"  # type: ignore[attr-defined]
            safety = "legacy"
            if idempotency and idempotency != "off":
                safety = f"idempotent:{idempotency}"
            self._register_route_or_rollback(
                kind="action",
                logical_id=logical_id,
                name=route_name,
                path=f"{self.prefix}{path}",
                methods=tuple(m.upper() for m in verb_list),
                operation_id=op_id,
                include_in_schema=include_in_schema,
                module=fn.__module__,
                tags=tuple(str(t) for t in (tags or ())),
                docs=inspect.getdoc(fn),
                endpoint=fn,
                htmx_inference={
                    "csrf": "required for unsafe cookie-authenticated methods",
                    "swap": "innerHTML",
                    "validation_fragment": "form error components",
                    "fragment_regions": _fragment_regions_for_inference(regions),
                    "capability": capability or "",
                    "action_safety": safety,
                },
            )
            return fn

        return decorator

    def include_component(
        self,
        descriptor: AddressableDescriptor[P, R] | Callable[P, R],
        *,
        path: str,
        name: str | None = None,
        dependencies: Sequence[params.Depends] | None = None,
        include_in_schema: bool | None = None,
        methods: Sequence[str] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **kwargs: Any,
    ) -> None:
        from hedron.responses import FragmentResponse

        if isinstance(descriptor, AddressableDescriptor):
            factory = descriptor.factory
            route_name = name or descriptor.name
            logical_id = descriptor.logical_id
            verb_list = list(methods or descriptor.methods)
            schema = (
                descriptor.include_in_schema if include_in_schema is None else include_in_schema
            )
            tag_list: list[str | Enum] = list(tags) if tags is not None else list(descriptor.tags)
        else:
            factory = descriptor
            route_name = name or factory.__name__
            logical_id = _logical_id(factory)
            verb_list = list(methods or ["GET"])
            schema = False if include_in_schema is None else include_in_schema
            tag_list = list(tags or [])

        regions = _normalize_fragment_regions(fragment_regions)
        factory._hedron_fragment_regions = regions  # type: ignore[attr-defined]
        op_id = operation_id_for("component", route_name, path, verb_list[0])
        wrapped = _wrap_endpoint(
            factory,
            kind="component",
            mode=RenderMode.FRAGMENT,
            require_csrf=_requires_csrf(verb_list),
            fragment_regions=regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
        self.add_api_route(
            path,
            wrapped,
            methods=verb_list,
            name=route_name,
            operation_id=op_id,
            include_in_schema=schema,
            dependencies=dependencies,
            tags=tag_list or None,
            response_class=kwargs.pop("response_class", None) or FragmentResponse,
            response_model=None,
            **kwargs,
        )
        self._register_route_or_rollback(
            kind="component",
            logical_id=logical_id,
            name=route_name,
            path=f"{self.prefix}{path}",
            methods=tuple(m.upper() for m in verb_list),
            operation_id=op_id,
            include_in_schema=schema,
            module=factory.__module__,
            tags=tuple(str(t) for t in tag_list),
            docs=inspect.getdoc(factory),
            endpoint=factory,
            htmx_inference={
                "default_mode": "fragment",
                "exposure": "include_component",
                "fragment_regions": _fragment_regions_for_inference(regions),
            },
        )
