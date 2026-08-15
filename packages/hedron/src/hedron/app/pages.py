"""Hedron page/component/fragment/action registration wrappers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any, ParamSpec, TypeVar

from hedron.routing.router import HedronRouter
from hedron_core.addressable import AddressableDescriptor
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
