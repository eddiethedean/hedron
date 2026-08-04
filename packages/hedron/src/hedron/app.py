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
from hedron_core.compile_gate import is_production_env
from hedron_core.theme import ensure_default_theme_registered

ExplorerMode = Literal["off", "development", "secured"]

_DEFAULT_SESSION_SECRET = "hedron-dev-secret-change-me"
logger = logging.getLogger("hedron")

__all__ = ["Hedron", "mount_build_assets", "mount_hedron_static"]


def _settings_explorer_hint() -> str | None:
    """Read explicit [tool.hedron] explorer from cwd when present."""
    try:
        import tomllib

        cwd = Path.cwd()
        pyproject = cwd / "pyproject.toml"
        if not pyproject.is_file():
            return None
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        tool = data.get("tool") or {}
        hedron = tool.get("hedron") if isinstance(tool, dict) else None
        if not isinstance(hedron, dict) or "explorer" not in hedron:
            return None
        mode = str(hedron["explorer"] or "off")
        if mode in {"off", "development", "secured"}:
            return mode
    except Exception:  # noqa: BLE001 — constructor must not fail on bad config
        return None
    return None


class Hedron(FastAPI):
    """Batteries-included FastAPI application with Hedron defaults."""

    def __init__(
        self,
        *args: Any,
        security: SecurityProfileName | str | SecurityPolicy = "standard",
        explorer: ExplorerMode | str | None = None,
        session_secret: str = _DEFAULT_SESSION_SECRET,
        enable_sessions: bool = True,
        explorer_dependencies: Sequence[Any] | None = None,
        theme: str | None = "default",
        default_styles: bool = True,
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
        # Explicit explorer= overrides policy.explorer_enabled; None follows policy,
        # then [tool.hedron] explorer when a project pyproject is present.
        if explorer is None:
            settings_explorer = _settings_explorer_hint()
            if settings_explorer is not None:
                self.hedron_explorer_mode = settings_explorer
            else:
                self.hedron_explorer_mode = (
                    "development" if self.hedron_policy.explorer_enabled else "off"
                )
        else:
            self.hedron_explorer_mode = str(explorer)

        is_prod = is_production_env(production=production)
        if is_prod and self.hedron_explorer_mode == "development":
            warnings.warn(
                "Explorer development mode is disabled in production; "
                "use explorer='secured' with explorer_dependencies, or explorer='off'.",
                UserWarning,
                stacklevel=2,
            )
            self.hedron_explorer_mode = "off"

        self.hedron_theme = theme
        self.hedron_default_styles = default_styles
        self.state.hedron_security = self.hedron_policy
        self.state.hedron_theme = theme
        self.state.hedron_default_styles = default_styles
        self.state.hedron_production = production if production is not None else is_prod
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

        from hedron.status_responses import install_interaction_handlers

        install_interaction_handlers(self)

        # Explorer bridges (ADP-005): injectable hooks avoid explorer→hedron imports.
        self.state.hedron_settings_loader = None
        try:
            from hedron.config import load_hedron_settings

            self.state.hedron_settings_loader = load_hedron_settings
        except Exception:  # noqa: BLE001
            pass
        try:
            from hedron.security.csrf import prepare_csrf_from_request, validate_csrf

            async def _csrf_validate(request: Request, policy: Any) -> None:
                await prepare_csrf_from_request(request, policy)
                validate_csrf(request, policy)

            self.state.hedron_csrf_validate = _csrf_validate
        except Exception:  # noqa: BLE001
            self.state.hedron_csrf_validate = None

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
