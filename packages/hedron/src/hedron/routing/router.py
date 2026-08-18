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


def _normalize_fragment_regions(
    fragment_regions: Sequence[FragmentRegion | str] | None,
) -> tuple[FragmentRegion, ...]:
    if not fragment_regions:
        return ()
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
        result = fn(*args, **kwargs)
        result = await await_if_needed(result)
        return await HedronRoute.convert_endpoint_result(
            request,
            result,  # type: ignore[arg-type]
            mode=mode,
            kind=kind,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )

    # Resolve annotations in the original function's globals so Depends survives wrapping.
    try:
        hints = typing.get_type_hints(fn, include_extras=True)
    except Exception:  # noqa: BLE001
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
        self._hedron_host_app: Any | None = None

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
            region_meta = {r.id: f"{r.selector}|{r.description}" for r in regions}
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
                    "fragment_regions": str(region_meta),
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
            region_meta = {r.id: f"{r.selector}|{r.description}" for r in regions}
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
                    "fragment_regions": str(region_meta),
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
            wrapped = _wrap_endpoint(
                fn,
                kind="action",
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
            route = self.routes[-1]
            if isinstance(route, HedronRoute):
                route.hedron_kind = "action"  # type: ignore[attr-defined]
            region_meta = tuple({"id": r.id, "selector": r.selector} for r in regions)
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
                    "fragment_regions": str(region_meta),
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
        region_meta = {r.id: f"{r.selector}|{r.description}" for r in regions}
        register_route(
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
                "fragment_regions": str(region_meta),
            },
        )
