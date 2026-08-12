"""Thin Hedron(FastAPI) application facade."""

from __future__ import annotations

import logging
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, Literal, ParamSpec, TypeVar

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.params import Depends as DependsParam
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from hedron.interaction import FragmentRegion
from hedron.lifespan import compose_lifespan
from hedron.openapi import install_openapi
from hedron.routing.router import HedronRouter
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.policy import SecurityPolicy, SecurityProfile, SecurityProfileName
from hedron.static_mount import mount_build_assets, mount_hedron_static
from hedron_core.addressable import AddressableDescriptor
from hedron_core.compile_gate import is_production_env
from hedron_core.theme import ensure_default_theme_registered

ExplorerMode = Literal["off", "development", "secured"]
P = ParamSpec("P")
R = TypeVar("R")

_DEFAULT_SESSION_SECRET = "hedron-dev-secret-change-me"
logger = logging.getLogger("hedron")

__all__ = ["Hedron", "mount_build_assets", "mount_hedron_static"]


def _settings_explorer_hint() -> str | None:
    """Read explicit [tool.hedron] explorer from cwd when present."""
    import tomllib

    try:
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
    except (OSError, TypeError, ValueError, KeyError, tomllib.TOMLDecodeError):
        return None
    return None


class Hedron(FastAPI):
    """Batteries-included FastAPI application with Hedron defaults.

    Installs session middleware (when enabled), CSRF-aware security profiles,
    security headers, bundled HTMX static assets, and a root ``HedronRouter`` for
    ``@page`` / ``@component`` / ``@action`` routes.

    Args:
        security: Built-in profile name (``development`` / ``standard`` / ``strict``)
            or a ``SecurityPolicy`` instance.
        explorer: Component Explorer mode (``off``, ``development``, ``secured``).
            ``None`` follows the security profile and optional ``[tool.hedron]`` settings.
        session_secret: Secret for Starlette session cookies. Replace the development
            default before production; ``strict`` requires an explicit value.
        enable_sessions: When ``True`` (default), install ``SessionMiddleware``.
        explorer_dependencies: FastAPI dependencies required for ``secured`` Explorer.
        theme: Registered theme name (``default`` when unchanged).
        default_styles: When ``True``, emit default theme styles on PAGE responses.
        build_dir: Optional precompiled asset manifest directory for production.
        production: Force production gate behavior; ``None`` follows ``HEDRON_ENV``.
        root_path: Optional construction-time mount (cookie Path / asset prefix).
            Wins over ``HEDRON_ROOT_PATH`` when set. ASGI ``root_path`` alone does
            not scope cookies.
        *args: Forwarded to ``FastAPI``.
        **kwargs: Forwarded to ``FastAPI`` (``lifespan`` is composed with Hedron gates).

    Examples:
        >>> app = Hedron(title="Demo", security="standard", session_secret="replace-me")
        >>> @app.page("/")
        ... def home() -> Page:  # doctest: +SKIP
        ...     return Page(Text("Hello"), title="Home")
    """

    def __init__(
        self,
        *args: Any,
        security: SecurityProfileName | str | SecurityPolicy = "standard",
        explorer: ExplorerMode | str | None = None,
        session_secret: str = _DEFAULT_SESSION_SECRET,
        enable_sessions: bool = True,
        explorer_dependencies: Sequence[DependsParam] | None = None,
        theme: str | None = "default",
        default_styles: bool = True,
        build_dir: str | Path | None = None,
        production: bool | None = None,
        root_path: str | None = None,
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

        from hedron_core.production_gate import (
            assert_durable_backends,
            assert_production_security_config,
        )

        assert_durable_backends(
            production=is_prod,
            strict_profile=self.hedron_policy.profile is SecurityProfile.STRICT,
        )
        assert_production_security_config(
            production=is_prod,
            security_profile=self.hedron_policy.profile.value,
            session_secret=session_secret if enable_sessions else None,
            explorer_mode=self.hedron_explorer_mode,
            allow_external_redirects=self.hedron_policy.allow_external_redirects,
            content_security_policy=self.hedron_policy.content_security_policy,
        )

        mount_cookie_path = "/"
        mount_was_configured = False
        try:
            from hedron.mount import normalize_mount_path, resolve_mount_path_from_environ

            if root_path is not None:
                mount_was_configured = True
                explicit = normalize_mount_path(root_path)
                mount_cookie_path = explicit if explicit else "/"
                self.state.hedron_mount_path = explicit
            else:
                env_mount = resolve_mount_path_from_environ()
                if env_mount is not None:
                    mount_was_configured = True
                    mount_cookie_path = env_mount.cookie_path
                    self.state.hedron_mount_path = env_mount.path
                else:
                    self.state.hedron_mount_path = ""
        except (ImportError, OSError, ValueError, TypeError) as exc:
            logger.debug("Mount path from environ unavailable: %s", exc)
            self.state.hedron_mount_path = ""
        self.state.hedron_mount_was_configured = mount_was_configured

        if enable_sessions:
            if (
                session_secret == _DEFAULT_SESSION_SECRET
                and self.hedron_policy.profile is SecurityProfile.STRICT
            ):
                raise ValueError(
                    "security='strict' requires an explicit session_secret "
                    "(do not use the development default)."
                )
            if session_secret == _DEFAULT_SESSION_SECRET and not is_prod:
                warnings.warn(
                    "Hedron is using the default development session_secret; "
                    "set session_secret explicitly before production deployment.",
                    UserWarning,
                    stacklevel=2,
                )
            self.add_middleware(
                SessionMiddleware,
                secret_key=session_secret,
                https_only=(
                    self.hedron_policy.profile is SecurityProfile.STRICT
                    or (is_prod and self.hedron_policy.profile is SecurityProfile.STANDARD)
                ),
                path=mount_cookie_path,
            )
        self.state.hedron_cookie_path = mount_cookie_path
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
        except ImportError:
            logger.debug("hedron.config unavailable; explorer settings bridge disabled")
        try:
            from hedron.security.csrf import prepare_csrf_from_request, validate_csrf

            async def _csrf_validate(request: Request, policy: SecurityPolicy) -> None:
                await prepare_csrf_from_request(request, policy)
                validate_csrf(request, policy)

            self.state.hedron_csrf_validate = _csrf_validate
        except ImportError:
            logger.debug("CSRF helpers unavailable; explorer CSRF bridge disabled")
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
        deps: list[DependsParam] = list(self._explorer_dependencies)
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
            if self._root_router.routes:
                route = self._root_router.routes[-1]
                if route not in self.router.routes:
                    self.router.routes.append(route)
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
            if self._root_router.routes:
                route = self._root_router.routes[-1]
                if route not in self.router.routes:
                    self.router.routes.append(route)
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
            if self._root_router.routes:
                route = self._root_router.routes[-1]
                if route not in self.router.routes:
                    self.router.routes.append(route)
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
        if self._root_router.routes:
            route = self._root_router.routes[-1]
            if route not in self.router.routes:
                self.router.routes.append(route)
