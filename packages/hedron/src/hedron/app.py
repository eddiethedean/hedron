"""Thin Hedron(FastAPI) application facade."""

from __future__ import annotations

from collections.abc import Callable
from importlib import resources
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from hedron.lifespan import compose_lifespan
from hedron.openapi import install_openapi
from hedron.routing.router import HedronRouter
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.policy import SecurityPolicy, SecurityProfileName

ExplorerMode = Literal["off", "development", "secured"]


class Hedron(FastAPI):
    """Batteries-included FastAPI application with Hedron defaults."""

    def __init__(
        self,
        *args: Any,
        security: SecurityProfileName | str | SecurityPolicy = "standard",
        explorer: ExplorerMode | str = "off",
        session_secret: str = "hedron-dev-secret-change-me",
        enable_sessions: bool = True,
        **kwargs: Any,
    ) -> None:
        user_lifespan = kwargs.pop("lifespan", None)
        kwargs.setdefault("lifespan", compose_lifespan(user_lifespan))
        super().__init__(*args, **kwargs)

        self.hedron_policy = SecurityPolicy.from_name(security)
        self.hedron_explorer_mode = str(explorer)
        self.state.hedron_security = self.hedron_policy

        if enable_sessions:
            self.add_middleware(SessionMiddleware, secret_key=session_secret)
        self.add_middleware(SecurityHeadersMiddleware, policy=self.hedron_policy)

        static_dir = Path(str(resources.files("hedron").joinpath("static")))
        if static_dir.is_dir():
            self.mount(
                "/hedron-static", StaticFiles(directory=str(static_dir)), name="hedron-static"
            )

        self._root_router = HedronRouter()
        install_openapi(self)

        if (
            self.hedron_explorer_mode == "development" and self.hedron_policy.explorer_enabled
        ) or self.hedron_explorer_mode == "secured":
            self._maybe_mount_explorer()

    def _maybe_mount_explorer(self) -> None:
        try:
            from hedron_explorer import explorer_router
        except ImportError:
            return
        self.include_router(explorer_router(), prefix="/hedron-explorer")

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        super().include_router(router, *args, **kwargs)

    def page(self, path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        decorator = self._root_router.page(path, **kwargs)

        def wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
            decorator(fn)
            # Re-include routes added to root router.
            if self._root_router.routes:
                route = self._root_router.routes[-1]
                if route not in self.router.routes:
                    self.router.routes.append(route)
            return fn

        return wrap

    def component(
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        decorator = self._root_router.component(path, **kwargs)

        def wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
            decorator(fn)
            if self._root_router.routes:
                route = self._root_router.routes[-1]
                if route not in self.router.routes:
                    self.router.routes.append(route)
            return fn

        return wrap

    def action(
        self, path: str, **kwargs: Any
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        decorator = self._root_router.action(path, **kwargs)

        def wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
            decorator(fn)
            if self._root_router.routes:
                route = self._root_router.routes[-1]
                if route not in self.router.routes:
                    self.router.routes.append(route)
            return fn

        return wrap

    def include_component(self, descriptor: Any, *, path: str, **kwargs: Any) -> None:
        self._root_router.include_component(descriptor, path=path, **kwargs)
        if self._root_router.routes:
            route = self._root_router.routes[-1]
            if route not in self.router.routes:
                self.router.routes.append(route)
