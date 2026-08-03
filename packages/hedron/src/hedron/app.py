"""Thin Hedron(FastAPI) application facade."""

from __future__ import annotations

import logging
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException, status
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from hedron.lifespan import compose_lifespan
from hedron.openapi import install_openapi
from hedron.routing.router import HedronRouter
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.policy import SecurityPolicy, SecurityProfile, SecurityProfileName
from hedron.static_mount import mount_build_assets, mount_hedron_static
from hedron_core.theme import ensure_default_theme_registered

ExplorerMode = Literal["off", "development", "secured"]

_DEFAULT_SESSION_SECRET = "hedron-dev-secret-change-me"
logger = logging.getLogger("hedron")

__all__ = ["Hedron", "mount_hedron_static", "mount_build_assets"]


class Hedron(FastAPI):
    """Batteries-included FastAPI application with Hedron defaults."""

    def __init__(
        self,
        *args: Any,
        security: SecurityProfileName | str | SecurityPolicy = "standard",
        explorer: ExplorerMode | str = "off",
        session_secret: str = _DEFAULT_SESSION_SECRET,
        enable_sessions: bool = True,
        explorer_dependencies: Sequence[Any] | None = None,
        theme: str | None = "default",
        build_dir: str | Path | None = None,
        production: bool | None = None,
        **kwargs: Any,
    ) -> None:
        user_lifespan = kwargs.pop("lifespan", None)
        kwargs.setdefault(
            "lifespan",
            compose_lifespan(
                user_lifespan,
                production=production,
                build_dir=build_dir,
                theme=theme,
            ),
        )
        super().__init__(*args, **kwargs)

        self.hedron_policy = SecurityPolicy.from_name(security)
        self.hedron_explorer_mode = str(explorer)
        self.hedron_theme = theme
        self.state.hedron_security = self.hedron_policy
        self.state.hedron_theme = theme
        self.state.hedron_production = production
        self._explorer_dependencies = list(explorer_dependencies or [])

        ensure_default_theme_registered()

        if enable_sessions:
            if (
                session_secret == _DEFAULT_SESSION_SECRET
                and self.hedron_policy.profile is SecurityProfile.STRICT
            ):
                raise ValueError(
                    "security='strict' requires an explicit session_secret "
                    "(do not use the development default)."
                )
            if session_secret == _DEFAULT_SESSION_SECRET:
                warnings.warn(
                    "Hedron is using the default development session_secret; "
                    "set session_secret explicitly before production deployment.",
                    UserWarning,
                    stacklevel=2,
                )
            self.add_middleware(SessionMiddleware, secret_key=session_secret)
        self.add_middleware(SecurityHeadersMiddleware, policy=self.hedron_policy)

        mount_hedron_static(self)
        mount_build_assets(self, build_dir)

        self._root_router = HedronRouter()
        install_openapi(self)

        if self.hedron_explorer_mode == "development":
            self._maybe_mount_explorer(secured=False)
        elif self.hedron_explorer_mode == "secured":
            self._maybe_mount_explorer(secured=True)

    def _maybe_mount_explorer(self, *, secured: bool) -> None:
        try:
            from hedron_explorer import explorer_router
        except ImportError:
            logger.warning("hedron-explorer is not installed; Explorer was not mounted")
            return
        deps: list[Any] = list(self._explorer_dependencies)
        if secured and not deps:

            async def _require_authenticated(request: Request) -> None:
                if not getattr(request.state, "hedron_authenticated", False):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Explorer requires authentication",
                    )

            deps.append(Depends(_require_authenticated))
        self.include_router(
            explorer_router(),
            prefix="/hedron-explorer",
            dependencies=deps or None,
        )

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        super().include_router(router, *args, **kwargs)

    def page(self, path: str, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        decorator = self._root_router.page(path, **kwargs)

        def wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
            decorator(fn)
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
