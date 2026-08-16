"""Hedron page/component/fragment/action registration wrappers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ParamSpec, TypeVar

from hedron.routing.router import HedronRouter
from hedron_core.addressable import AddressableDescriptor
from hedron_core.hosts import FragmentHost
from hedron_core.interaction import FragmentRegion

P = ParamSpec("P")
R = TypeVar("R")


class HedronPagesMixin:
    """Mixin that binds HedronRouter decorators onto the FastAPI application."""

    _root_router: HedronRouter
    router: Any

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
            self._sync_root_route()
            return fn

        return wrap

    def component(
        self,
        path: str,
        *,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Register an addressable component / fragment route.

        Args:
            path: URL path (FastAPI path syntax).
            fragment_regions: Declared HTMX fragment regions authorized for this route.
            **kwargs: Forwarded to ``HedronRouter.component`` / FastAPI route options.

        Returns:
            Decorator that registers the handler and returns it unchanged.
        """
        decorator = self._root_router.component(path, fragment_regions=fragment_regions, **kwargs)

        def wrap(fn: Callable[P, R]) -> Callable[P, R]:
            decorator(fn)
            self._sync_root_route()
            return fn

        return wrap

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

    def fragment(
        self,
        path: str,
        *,
        region: FragmentRegion | str | None = None,
        regions: Sequence[FragmentRegion | str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Alias of :meth:`component` that merges ``region`` / ``regions`` into the allowlist.

        Args:
            path: URL path (FastAPI path syntax).
            region: Single authorized region.
            regions: Additional authorized regions.
            fragment_regions: Explicit allowlist merged with ``region`` / ``regions``.
            **kwargs: Forwarded to :meth:`component`.

        Returns:
            Decorator that registers the fragment handler.
        """
        merged: list[FragmentRegion | str] = []
        if region is not None:
            merged.append(region)
        if regions is not None:
            merged.extend(regions)
        if fragment_regions is not None:
            merged.extend(fragment_regions)
        return self.component(path, fragment_regions=merged or None, **kwargs)

    def action(self, path: str, **kwargs: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Register a mutation endpoint (typically POST) with CSRF when profiles require it.

        Args:
            path: URL path (FastAPI path syntax).
            **kwargs: Forwarded to ``HedronRouter.action`` (for example ``method=\"POST\"``).

        Returns:
            Decorator that registers the action handler.
        """
        decorator = self._root_router.action(path, **kwargs)

        def wrap(fn: Callable[P, R]) -> Callable[P, R]:
            decorator(fn)
            self._sync_root_route()
            return fn

        return wrap

    def include_component(
        self,
        descriptor: AddressableDescriptor[P, R] | Callable[P, R],
        *,
        path: str,
        **kwargs: Any,
    ) -> None:
        self._root_router.include_component(descriptor, path=path, **kwargs)
        self._sync_root_route()

    def refreshable(
        self,
        path: str | Callable[P, R] | None = None,
        *,
        key: str | None = None,
        name: str | None = None,
        host: FragmentHost | None = None,
        loading: Any = None,
        error: Any = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Register a GET renderer and return a ``FragmentHandle``."""
        if callable(path):
            return self.refreshable(
                None,
                key=key,
                name=name,
                host=host,
                loading=loading,
                error=error,
                fallback=fallback,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                **kwargs,
            )(path)

        def decorator(fn: Callable[P, R]) -> Any:
            from hedron.handles import build_view_handle, wrap_endpoint_result

            app_id = str(getattr(self, "hedron_app_id", "") or "")
            mount = str(getattr(getattr(self, "state", None), "hedron_mount_path", "") or "")
            view_host = host or FragmentHost()
            if loading is not None:
                view_host._loading = loading
            if error is not None:
                view_host._error = error
            handle = build_view_handle(
                fn,
                app_id=app_id,
                path=path if isinstance(path, str) else None,
                key=key,
                name=name,
                host=view_host,
                fallback=fallback,
                include_in_schema=include_in_schema,
                mount_path=mount,
            )
            endpoint = wrap_endpoint_result(handle)
            self._root_router.component(
                handle.path,
                fragment_regions=(handle.region,),
                name=handle.name,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                **kwargs,
            )(endpoint)
            self._sync_root_route()
            state = getattr(self, "state", None)
            handles = getattr(state, "hedron_handles", None)
            if handles is None and state is not None:
                state.hedron_handles = {}
                handles = state.hedron_handles
            if isinstance(handles, dict):
                handles[handle.logical_id] = handle
            return handle

        return decorator

    def command(
        self,
        path: str | Callable[P, R] | None = None,
        *,
        method: str = "POST",
        name: str | None = None,
        fallback: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Register a mutation and return an ``ActionHandle``."""
        if callable(path):
            return self.command(
                None,
                method=method,
                name=name,
                fallback=fallback,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                **kwargs,
            )(path)

        def decorator(fn: Callable[P, R]) -> Any:
            import contextlib
            import functools
            import inspect

            from starlette.responses import PlainTextResponse, RedirectResponse

            from hedron.async_utils import await_if_needed
            from hedron.handles import build_command_handle
            from hedron.routing.router import current_request
            from hedron_core.codes import HED_CMD_0002
            from hedron_core.updates import Patch, PatchSet, RefreshIntent

            app_id = str(getattr(self, "hedron_app_id", "") or "")
            mount = str(getattr(getattr(self, "state", None), "hedron_mount_path", "") or "")
            handle = build_command_handle(
                fn,
                app_id=app_id,
                path=path if isinstance(path, str) else None,
                method=method,
                name=name,
                fallback=fallback,
                include_in_schema=include_in_schema,
                mount_path=mount,
            )

            @functools.wraps(fn)
            async def endpoint(*args: Any, **kw: Any) -> Any:
                result = await await_if_needed(fn(*args, **kw))
                request = current_request.get()
                is_htmx = bool(
                    request is not None
                    and str(request.headers.get("HX-Request") or "").lower() == "true"
                )
                update = isinstance(result, (RefreshIntent, Patch, PatchSet))
                if not is_htmx and update:
                    if handle.fallback:
                        return RedirectResponse(handle.fallback, status_code=303)
                    return PlainTextResponse(HED_CMD_0002, status_code=400)
                return result

            with contextlib.suppress(TypeError, ValueError):
                endpoint.__signature__ = inspect.signature(fn)  # type: ignore[attr-defined]
            self._root_router.action(
                handle.path,
                method=handle.method,
                name=handle.name,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                allow_undeclared_targets=True,
                **kwargs,
            )(endpoint)
            self._sync_root_route()
            state = getattr(self, "state", None)
            handles = getattr(state, "hedron_handles", None)
            if handles is None and state is not None:
                state.hedron_handles = {}
                handles = state.hedron_handles
            if isinstance(handles, dict):
                handles[handle.logical_id] = handle
            return handle

        return decorator
