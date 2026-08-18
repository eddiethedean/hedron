"""Hedron(FastAPI) application subclass and constructor wiring."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.params import Depends as DependsParam

from hedron.app.explorer import (
    ExplorerMode,
    install_explorer_bridges,
    mount_explorer_if_enabled,
    resolve_explorer_mode,
)
from hedron.app.pages import HedronPagesMixin
from hedron.app.sessions import DEFAULT_SESSION_SECRET, configure_sessions
from hedron.lifespan import compose_lifespan
from hedron.openapi import install_openapi
from hedron.routing.router import HedronRouter
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.policy import SecurityPolicy, SecurityProfile, SecurityProfileName
from hedron.static_mount import mount_build_assets, mount_hedron_static
from hedron_core.compile_gate import is_production_env
from hedron_core.theme import ensure_default_theme_registered

logger = logging.getLogger("hedron")

__all__ = ["Hedron"]


class Hedron(HedronPagesMixin, FastAPI):
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
            ``None`` is refused when ``enable_sessions`` is ``True``.
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
        session_secret: str | None = DEFAULT_SESSION_SECRET,
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

        import secrets

        self.hedron_policy = SecurityPolicy.from_name(security)
        self.hedron_app_id = secrets.token_hex(8)
        self.state.hedron_app_id = self.hedron_app_id
        is_prod = is_production_env(production=production)
        self.hedron_explorer_mode = resolve_explorer_mode(
            explorer,
            explorer_enabled=self.hedron_policy.explorer_enabled,
            is_prod=is_prod,
        )

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
            session_secret=session_secret,
            sessions_enabled=enable_sessions,
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

        configure_sessions(
            self,
            session_secret=session_secret,
            enable_sessions=enable_sessions,
            is_prod=is_prod,
            mount_cookie_path=mount_cookie_path,
        )
        self.add_middleware(SecurityHeadersMiddleware, policy=self.hedron_policy)

        mount_hedron_static(self)
        mount_build_assets(self, build_dir)

        self._root_router = HedronRouter()
        self._root_router._hedron_host_app = self
        install_openapi(self)

        from hedron.status_responses import install_interaction_handlers

        install_interaction_handlers(self)

        install_explorer_bridges(self)

        mount_explorer_if_enabled(
            self,
            explorer_mode=self.hedron_explorer_mode,
            explorer_dependencies=self._explorer_dependencies,
        )

    @property
    def interactions(self) -> object:
        """Read-only interaction catalog for this application."""
        from hedron.interactions import app_interactions

        return app_interactions(self)

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        from hedron.registration import fail_closed_late_registration
        from hedron_core.catalog import get_sealed_catalog
        from hedron_core.registry.builder import active_builder

        builder = active_builder()
        fail_closed_late_registration(
            registry_sealed=builder._sealed,
            catalog_sealed=get_sealed_catalog() is not None,
            openapi_cached=self.openapi_schema is not None,
        )
        if isinstance(router, HedronRouter):
            router._hedron_host_app = self
        super().include_router(router, *args, **kwargs)
