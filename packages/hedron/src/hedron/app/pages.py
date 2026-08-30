"""Hedron page/view/action registration wrappers."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from contextlib import AbstractContextManager, nullcontext
from typing import TYPE_CHECKING, Any, ParamSpec, Protocol, TypeVar, cast, overload

from fastapi import FastAPI, params
from fastapi.routing import APIRouter

from hedron.fastapi_compat import cached_openapi
from hedron.handles import ActionHandle, FragmentHandle, as_node_like
from hedron.routing.router import HedronRouter
from hedron.type_authoring.classes import CommandHandler, RefreshableView
from hedron.type_authoring.normalize import CompiledTypeHandler
from hedron_core.addressable import AddressableDescriptor
from hedron_core.bundles import FeatureBundle, FeatureProvider
from hedron_core.component import NodeLike
from hedron_core.hosts import FragmentHost
from hedron_core.htmx.policy import CacheHint
from hedron_core.identifiers import component_type_id
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.updates import Patch, PatchSet, RefreshIntent

if TYPE_CHECKING:
    from hedron.runtime import HedronRuntimeContext

P = ParamSpec("P")
R = TypeVar("R")


class _HandleState(Protocol):
    hedron_handles: dict[str, object]


def _route_dependencies(
    dependencies: Sequence[params.Depends] | Sequence[object] | None,
) -> Sequence[params.Depends] | None:
    """Router APIs accept Depends only; callers may pass a wider sequence type."""
    if dependencies is None:
        return None
    return cast(Sequence[params.Depends], dependencies)


def _stamp(obj: object, **attrs: object) -> None:
    """Attach dynamic handler metadata without Any-casts."""
    for name, value in attrs.items():
        setattr(obj, name, value)


def _store_handle(state: object | None, logical_id: str, handle: object) -> None:
    """Store a generated handle on Starlette's dynamically typed application state."""
    if state is None:
        return
    existing: object = getattr(state, "hedron_handles", None)
    if existing is None:
        existing = {}
        cast(_HandleState, state).hedron_handles = existing
    if isinstance(existing, dict):
        cast(dict[str, object], existing)[logical_id] = handle


def _apply_mapped_outcome(
    mapped: object,
    status: int,
    case_effects: object,
    *,
    meta: CompiledTypeHandler | None,
    app_id: str,
) -> object:
    from hedron.handles import refresh
    from hedron.type_authoring import assert_declared_effects
    from hedron.type_authoring.markers import Refreshes
    from hedron_core.updates import compile_to_interaction

    effect_result: object = mapped
    if isinstance(case_effects, Refreshes):
        effect_result = refresh(*case_effects.targets)
    assert_declared_effects(
        meta,
        effect_result,
        app_id=app_id,
    )
    if isinstance(effect_result, (RefreshIntent, Patch, PatchSet)):
        compiled = compile_to_interaction(cast(object, effect_result), expected_app_id=app_id)
        if isinstance(compiled, InteractionResult):
            content = (
                mapped
                if not isinstance(mapped, (RefreshIntent, Patch, PatchSet, InteractionResult))
                else compiled.content
            )
            return InteractionResult(
                content=as_node_like(content) if content is not None else None,
                status_code=status,
                trigger=compiled.trigger,
                oob=compiled.oob,
                policy=compiled.policy,
                explanation=compiled.explanation,
            )
    if status != 200 and not isinstance(
        mapped, (RefreshIntent, Patch, PatchSet, InteractionResult)
    ):
        return InteractionResult(content=as_node_like(mapped), status_code=status)
    return cast(object, mapped)


class HedronPagesMixin:
    """Mixin that binds HedronRouter decorators onto the FastAPI application."""

    _root_router: HedronRouter
    _hedron_runtime: HedronRuntimeContext
    router: APIRouter

    def _runtime_scope(self) -> AbstractContextManager[None]:
        runtime = getattr(self, "_hedron_runtime", None)
        return runtime.activate() if runtime is not None else nullcontext()

    def _sync_root_route(self) -> None:
        if self._root_router.routes:
            route = self._root_router.routes[-1]
            if route not in self.router.routes:
                self.router.routes.append(route)

    def page(
        self,
        path: str,
        *,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Register a navigable PAGE route.

        Args:
            path: URL path (FastAPI path syntax).
            fragment_regions: Declared HTMX fragment regions authorized for this route.
            **kwargs: Forwarded to ``HedronRouter.page`` / FastAPI route options.

        Returns:
            Decorator that registers the handler and returns it unchanged.
        """
        decorator = self._root_router.page(path, fragment_regions=fragment_regions, **kwargs)

        def wrap(fn: Callable[P, R]) -> Callable[P, R]:
            decorator(fn)
            # FeatureBundle materialization needs a stable identity for page
            # factories, while ordinary page authoring remains function-only.
            _stamp(
                fn,
                logical_id=component_type_id(
                    "hedron",
                    getattr(fn, "__module__", "hedron"),
                    getattr(fn, "__name__", "page"),
                ),
                path=path,
            )
            self._sync_root_route()
            return fn

        return wrap

    @overload
    def view(
        self,
        path: Callable[..., Any] | type[RefreshableView[Any, Any]],
        *,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        **kwargs: Any,
    ) -> FragmentHandle[Any, Any]: ...

    @overload
    def view(
        self,
        path: str | None = None,
        *,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], FragmentHandle[Any, Any]]: ...

    def view(
        self,
        path: str | Callable[P, R] | type[RefreshableView[Any, Any]] | None = None,
        *,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        **kwargs: Any,
    ) -> FragmentHandle[Any, Any] | Callable[[Callable[..., Any]], FragmentHandle[Any, Any]]:
        """Register the canonical safe replaceable view and return its handle.

        The 1.0 view surface owns the route, target, binding, and lifecycle
        metadata.  ``HedronRouter.view`` remains the lower-level route
        decorator for applications that explicitly choose the Advanced router
        integration surface.
        """
        if fragment_regions is not None:
            kwargs["fragment_regions"] = fragment_regions
        if callable(path):
            with self._runtime_scope():
                return self._view(path, **kwargs)
        decorator = self._view(path, **kwargs)

        def scoped(fn: Callable[..., Any]) -> FragmentHandle[Any, Any]:
            with self._runtime_scope():
                return decorator(fn)

        return scoped

    def region(
        self,
        id: str,
        *,
        selector: str | None = None,
        description: str = "",
    ) -> FragmentRegion:
        """Declare a fragment region (default selector ``#{id}``).

        Args:
            id: Stable region identifier used in markup and allowlists.
            selector: CSS selector for the swap target; defaults to ``#{id}``.
            description: Human-readable description for Explorer / diagnostics.

        Returns:
            A ``FragmentRegion`` value for ``RefreshButton.for_region`` / ``@fragment``.
        """
        return FragmentRegion(id=id, selector=selector or f"#{id}", description=description)

    def action(
        self,
        path: str,
        *,
        method: str = "POST",
        fallback: str | None = None,
        include_in_schema: bool = True,
        **kwargs: Any,
    ) -> Callable[[Callable[P, object]], ActionHandle[Any, Any]]:
        """Register the canonical typed mutation and return an ``ActionHandle``.

        Args:
            path: URL path (FastAPI path syntax).
            method: Unsafe HTTP verb, ``POST`` by default.
            fallback: Optional ordinary HTTP fallback path.
            include_in_schema: Include the action in OpenAPI (``True`` by default).
            **kwargs: Canonical action options such as ``fragment_regions``,
                ``authorization``, ``idempotency``, and ``outcomes``.

        Returns:
            A decorator that returns an ``ActionHandle`` after registration.
        """
        simulator_options = {
            "accumulate",
            "empty",
            "list_remove",
            "methods",
            "region",
            "regions",
            "sequence",
            "validate",
            "variants",
        }
        if simulator_options.intersection(kwargs):
            names = ", ".join(sorted(simulator_options.intersection(kwargs)))
            raise TypeError(
                f"Hedron.action does not accept simulator-only options ({names}); "
                "use hedron_sim.SimApp.action for offline demo routes."
            )
        decorator = self._action(
            path,
            method=method,
            fallback=fallback,
            include_in_schema=include_in_schema,
            **kwargs,
        )

        def scoped(fn: Callable[P, object]) -> ActionHandle[Any, Any]:
            with self._runtime_scope():
                return decorator(fn)

        return scoped

    def include_component(
        self,
        descriptor: AddressableDescriptor[P, R] | Callable[P, R],
        *,
        path: str,
        **kwargs: Any,
    ) -> None:
        from hedron.registration import fail_closed_late_registration
        from hedron_core.catalog import get_sealed_catalog
        from hedron_core.registry.builder import active_builder

        builder = active_builder()
        fail_closed_late_registration(
            registry_sealed=builder.is_sealed,
            catalog_sealed=get_sealed_catalog() is not None,
            openapi_cached=cached_openapi(cast(FastAPI, self)) is not None,
        )
        with self._runtime_scope():
            self._root_router.include_component(descriptor, path=path, **kwargs)
            self._sync_root_route()

    def include(
        self,
        feature: FeatureBundle | FeatureProvider,
        *,
        capabilities: Mapping[str, bool] | None = None,
    ) -> FeatureBundle:
        """Include one feature bundle through the canonical 1.0 spelling."""
        from hedron.features import include_feature as _include

        with self._hedron_runtime.activate():
            return _include(self, feature, capabilities=capabilities)

    @overload
    def _view(
        self,
        path: Callable[..., Any] | type[RefreshableView[Any, Any]],
        *,
        key: str | None = None,
        name: str | None = None,
        host: FragmentHost | None = None,
        loading: NodeLike | None = None,
        error: NodeLike | str | None = None,
        empty: NodeLike | None = None,
        cache: CacheHint | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | Sequence[object] | None = None,
        **kwargs: Any,
    ) -> FragmentHandle[Any, Any]: ...

    @overload
    def _view(
        self,
        path: str | None = None,
        *,
        key: str | None = None,
        name: str | None = None,
        host: FragmentHost | None = None,
        loading: NodeLike | None = None,
        error: NodeLike | str | None = None,
        empty: NodeLike | None = None,
        cache: CacheHint | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | Sequence[object] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], FragmentHandle[Any, Any]]: ...

    def _view(
        self,
        path: str | Callable[P, R] | type[RefreshableView[Any, Any]] | None = None,
        *,
        key: str | None = None,
        name: str | None = None,
        host: FragmentHost | None = None,
        loading: NodeLike | None = None,
        error: NodeLike | str | None = None,
        empty: NodeLike | None = None,
        cache: CacheHint | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | Sequence[object] | None = None,
        **kwargs: Any,
    ) -> FragmentHandle[Any, Any] | Callable[[Callable[..., Any]], FragmentHandle[Any, Any]]:
        """Register a GET renderer and return a ``FragmentHandle``."""
        import inspect

        if inspect.isclass(path):
            from hedron.type_authoring import (
                class_config_conflict,
                compile_view_class,
            )

            # compile_view_class validates RefreshableView; keep that error path.
            view_cls = path
            class_config_conflict(
                view_cls,
                decorator_fallback=fallback,
                decorator_path=None,
            )
            compiled = compile_view_class(view_cls)  # type: ignore[arg-type]
            register = self._view(
                None,
                key=key,
                name=name or getattr(view_cls, "__name__", None),
                host=host or getattr(view_cls, "host", None),
                loading=loading if loading is not None else getattr(view_cls, "loading", None),
                error=error if error is not None else getattr(view_cls, "error", None),
                empty=empty if empty is not None else getattr(view_cls, "empty", None),
                cache=cache if cache is not None else getattr(view_cls, "cache", None),
                fallback=fallback or getattr(view_cls, "fallback", None),
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                **kwargs,
            )
            return register(compiled)

        if callable(path):
            register = self._view(
                None,
                key=key,
                name=name,
                host=host,
                loading=loading,
                error=error,
                empty=empty,
                cache=cache,
                fallback=fallback,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                **kwargs,
            )
            return register(path)

        def decorator(fn: Callable[..., Any]) -> FragmentHandle[Any, Any]:
            import inspect

            from hedron.handles import build_view_handle, wrap_endpoint_result
            from hedron.type_authoring import class_config_conflict, compile_view_class

            resolved_host = host
            resolved_loading = loading
            resolved_error = error
            resolved_empty = empty
            resolved_cache = cache
            resolved_fallback = fallback
            handler: Callable[..., Any] = fn
            if inspect.isclass(fn):
                class_config_conflict(fn, decorator_fallback=fallback, decorator_path=path)
                resolved_host = host or getattr(fn, "host", None)
                resolved_loading = loading if loading is not None else getattr(fn, "loading", None)
                resolved_error = error if error is not None else getattr(fn, "error", None)
                resolved_empty = empty if empty is not None else getattr(fn, "empty", None)
                resolved_cache = cache if cache is not None else getattr(fn, "cache", None)
                resolved_fallback = fallback or getattr(fn, "fallback", None)
                handler = compile_view_class(fn)  # type: ignore[arg-type]

            app_id = str(getattr(self, "hedron_app_id", "") or "")
            mount = str(getattr(getattr(self, "state", None), "hedron_mount_path", "") or "")
            view_host = resolved_host or FragmentHost()
            if resolved_loading is not None:
                view_host.loading = resolved_loading
            if resolved_error is not None:
                view_host.error_content = resolved_error
            if resolved_empty is not None:
                view_host.empty_content = resolved_empty
            if resolved_cache is not None:
                view_host.cache = resolved_cache
            handle = build_view_handle(
                handler,
                app_id=app_id,
                path=path if isinstance(path, str) else None,
                key=key,
                name=name,
                host=view_host,
                fallback=resolved_fallback,
                include_in_schema=include_in_schema,
                mount_path=mount,
            )
            endpoint = wrap_endpoint_result(handle)
            extra_regions = kwargs.pop("fragment_regions", None)
            from hedron.routing.router import normalize_fragment_regions

            regions = (handle.region, *normalize_fragment_regions(extra_regions))
            self._root_router.view(
                handle.path,
                fragment_regions=regions,
                name=handle.name,
                include_in_schema=include_in_schema,
                dependencies=_route_dependencies(dependencies),
                **kwargs,
            )(endpoint)
            self._sync_root_route()
            state = getattr(self, "state", None)
            _store_handle(state, handle.logical_id, handle)
            return handle

        return decorator

    @overload
    def _action(
        self,
        path: Callable[..., Any] | type[CommandHandler[Any, Any]],
        *,
        method: str = "POST",
        name: str | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | Sequence[object] | None = None,
        outcomes: object | None = None,
        **kwargs: Any,
    ) -> ActionHandle[Any, Any]: ...

    @overload
    def _action(
        self,
        path: str | None = None,
        *,
        method: str = "POST",
        name: str | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | Sequence[object] | None = None,
        outcomes: object | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any]], ActionHandle[Any, Any]]: ...

    def _action(
        self,
        path: str | Callable[P, R] | type[CommandHandler[Any, Any]] | None = None,
        *,
        method: str = "POST",
        name: str | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | Sequence[object] | None = None,
        outcomes: object | None = None,
        **kwargs: Any,
    ) -> ActionHandle[Any, Any] | Callable[[Callable[..., Any]], ActionHandle[Any, Any]]:
        """Register a mutation and return an ``ActionHandle``."""
        import inspect

        authorization = kwargs.pop("authorization", None)
        if inspect.isclass(path):
            from hedron.type_authoring import (
                class_config_conflict,
                compile_command_class,
            )

            command_cls = path
            class_config_conflict(command_cls, decorator_fallback=fallback, decorator_path=None)
            compiled = compile_command_class(command_cls)  # type: ignore[arg-type]
            _stamp(
                compiled,
                __hedron_outcomes__=getattr(command_cls, "outcomes", None) or outcomes,
                __hedron_effects__=getattr(command_cls, "effects", None),
            )
            register = self._action(
                None,
                method=method,
                name=name or getattr(command_cls, "__name__", None),
                fallback=fallback or getattr(command_cls, "fallback", None),
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                authorization=authorization,
                outcomes=outcomes,
                **kwargs,
            )
            return register(compiled)

        if callable(path):
            register = self._action(
                None,
                method=method,
                name=name,
                fallback=fallback,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                authorization=authorization,
                outcomes=outcomes,
                **kwargs,
            )
            return register(path)

        def decorator(fn: Callable[..., Any]) -> ActionHandle[Any, Any]:
            import contextlib
            import functools
            import inspect

            from starlette.responses import PlainTextResponse

            from hedron.async_utils import await_if_needed
            from hedron.handles import build_command_handle
            from hedron.routing.router import current_request
            from hedron.security.redirects import redirect_local
            from hedron.type_authoring import (
                apply_modeled_signature,
                assert_declared_effects,
                class_config_conflict,
                compile_command_class,
                reconstruct_kwargs,
            )
            from hedron.type_authoring.signature import formbody_media_types, reject_json_formbody
            from hedron_core.codes import HED_CMD_0002
            from hedron_core.interaction import InteractionResult
            from hedron_core.updates import Patch, PatchSet, RefreshIntent

            resolved_fallback = fallback
            handler: Callable[..., Any] = fn
            if inspect.isclass(fn):
                class_config_conflict(fn, decorator_fallback=fallback, decorator_path=path)
                compiled_fn = compile_command_class(fn)  # type: ignore[arg-type]
                _stamp(
                    compiled_fn,
                    __hedron_outcomes__=getattr(fn, "outcomes", None) or outcomes,
                    __hedron_effects__=getattr(fn, "effects", None),
                )
                resolved_fallback = fallback or getattr(fn, "fallback", None)
                handler = compiled_fn
            elif outcomes is not None and getattr(fn, "__hedron_outcomes__", None) is None:
                _stamp(fn, __hedron_outcomes__=outcomes)

            app_id = str(getattr(self, "hedron_app_id", "") or "")
            mount = str(getattr(getattr(self, "state", None), "hedron_mount_path", "") or "")
            handle = build_command_handle(
                handler,
                app_id=app_id,
                path=path if isinstance(path, str) else None,
                method=method,
                name=name,
                fallback=resolved_fallback,
                include_in_schema=include_in_schema,
                mount_path=mount,
            )

            @functools.wraps(handler)
            async def endpoint(*args: Any, **kw: Any) -> Any:
                call_kw = dict(kw)
                meta = handle.type_meta
                if meta is not None and getattr(meta, "modeled", False):
                    reject_json_formbody(meta, current_request.get())
                    call_kw = reconstruct_kwargs(meta, call_kw)
                result = await await_if_needed(handler(*args, **call_kw))
                outcomes_map = getattr(meta, "outcomes", None) if meta is not None else None
                if outcomes_map is not None:
                    mapped, status, case_effects = outcomes_map.map_result(result)
                    result = _apply_mapped_outcome(
                        mapped, status, case_effects, meta=meta, app_id=app_id
                    )
                else:
                    assert_declared_effects(meta, result, app_id=app_id)
                from hedron.handles import apply_action_handle_effects

                result = apply_action_handle_effects(
                    result,
                    handle,
                    app_id=app_id,
                )
                request = current_request.get()
                is_htmx = bool(
                    request is not None
                    and str(request.headers.get("HX-Request") or "").lower() == "true"
                )
                update = isinstance(result, (RefreshIntent, Patch, PatchSet, InteractionResult))
                if not is_htmx and update and isinstance(result, (RefreshIntent, Patch, PatchSet)):
                    if handle.fallback:
                        return redirect_local(handle.fallback, status_code=303)
                    return PlainTextResponse(HED_CMD_0002, status_code=400)
                return result

            if authorization is not None:
                _stamp(endpoint, _hedron_requires_scopes=authorization)
            meta = handle.type_meta
            if meta is not None:
                media = formbody_media_types(meta)
                if media:
                    _stamp(endpoint, _hedron_form_media=media)
            with contextlib.suppress(TypeError, ValueError):
                if meta is not None:
                    _stamp(endpoint, __signature__=apply_modeled_signature(handler, meta))
                else:
                    from hedron.type_authoring.signature import compile_injected_depends

                    _stamp(
                        endpoint,
                        __signature__=compile_injected_depends(inspect.signature(handler)),
                    )
            from hedron.routing.router import normalize_fragment_regions

            extra_regions = kwargs.pop("fragment_regions", None)
            regions = (handle.region, *normalize_fragment_regions(extra_regions))
            self._root_router.action(
                handle.path,
                method=handle.method,
                name=handle.name,
                include_in_schema=include_in_schema,
                dependencies=_route_dependencies(dependencies),
                fragment_regions=regions,
                **kwargs,
            )(endpoint)
            self._sync_root_route()
            state = getattr(self, "state", None)
            _store_handle(state, handle.logical_id, handle)
            return handle

        return decorator
