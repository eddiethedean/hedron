"""Hedron(FastAPI) application subclass and constructor wiring."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.params import Depends as DependsParam

from hedron.app.bootstrap import (
    HedronBootstrapConfig,
    HedronBootstrapper,
    HedronBootstrapStep,
    normalize_theme_selection,
)
from hedron.app.explorer import ExplorerMode
from hedron.app.pages import HedronPagesMixin
from hedron.app.sessions import DEFAULT_SESSION_SECRET
from hedron.concurrency import ConcurrencyConfig, ConcurrencyLimiter
from hedron.fastapi_compat import cached_openapi
from hedron.lifespan import compose_lifespan
from hedron.routing.router import HedronRouter
from hedron.runtime import HedronRuntimeContext, RuntimeContextMiddleware
from hedron.security.policy import SecurityPolicy, SecurityProfileName
from hedron.tracing import TraceConfig
from hedron_core.cache.backend import CacheBackend
from hedron_core.design_system import DesignSystem
from hedron_core.jobs.backend import JobBackend
from hedron_core.theme import Theme

__all__ = ["Hedron"]


class Hedron(HedronPagesMixin, FastAPI):
    """Batteries-included FastAPI application with Hedron defaults.

    Installs session middleware (when enabled), CSRF-aware security profiles,
    security headers, bundled HTMX static assets, and a root ``HedronRouter`` for
    ``@page`` / ``@view`` / ``@action`` routes.

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
        theme: Registered theme name, ``Theme``, ``DesignSystem``, or ``None``
            (no construction-time selection; lifespan may still default).
        default_styles: When ``True``, emit default theme styles on PAGE responses.
        demand_driven_assets: When ``True``, emit HTMX, Alpine, UI, and specialist browser
            assets only when the rendered document declares the corresponding capability.
            ``False`` preserves the 1.0 eager-asset compatibility behavior.
        build_dir: Optional precompiled asset manifest directory for production.
        production: Force production gate behavior; ``None`` follows ``HEDRON_ENV``.
        root_path: Optional construction-time mount (cookie Path / asset prefix).
            Wins over ``HEDRON_ROOT_PATH`` when set. ASGI ``root_path`` alone does
            not scope cookies.
        bootstrap_steps: Optional extension steps run after Hedron's mandatory
            identity, security, middleware, routing, and integration setup.
        cache_backend: Application-owned cache backend. If omitted, an isolated
            in-memory backend is created for this application.
        job_backend: Application-owned job backend. If omitted, an isolated
            in-memory backend is created for this application.
        concurrency_config: Application-owned concurrency policy.
        tracing_config: Application-owned tracing policy.
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
        theme: str | Theme | DesignSystem | None = "default",
        default_styles: bool = True,
        demand_driven_assets: bool = False,
        build_dir: str | Path | None = None,
        production: bool | None = None,
        root_path: str | None = None,
        bootstrap_steps: Sequence[HedronBootstrapStep] | None = None,
        cache_backend: CacheBackend | None = None,
        job_backend: JobBackend | None = None,
        concurrency_config: ConcurrencyConfig | None = None,
        tracing_config: TraceConfig | None = None,
        **kwargs: Any,
    ) -> None:
        self._hedron_runtime = HedronRuntimeContext.from_defaults()
        if cache_backend is not None:
            self._hedron_runtime.cache = cache_backend
        if job_backend is not None:
            self._hedron_runtime.jobs = job_backend
        if concurrency_config is not None:
            self._hedron_runtime.concurrency = concurrency_config
            self._hedron_runtime.limiter = ConcurrencyLimiter(concurrency_config)
        if tracing_config is not None:
            self._hedron_runtime.tracing = tracing_config
        user_lifespan = kwargs.pop("lifespan", None)
        with self._hedron_runtime.activate():
            resolved_theme, design_system = normalize_theme_selection(theme)
            kwargs.setdefault(
                "lifespan",
                compose_lifespan(
                    user_lifespan,
                    production=production,
                    build_dir=build_dir,
                    theme=resolved_theme,
                ),
            )
            super().__init__(*args, **kwargs)
            self._explorer_dependencies = (
                list(explorer_dependencies) if explorer_dependencies is not None else []
            )
            config = HedronBootstrapConfig(
                security=security,
                explorer=explorer,
                session_secret=session_secret,
                enable_sessions=enable_sessions,
                explorer_dependencies=tuple(self._explorer_dependencies),
                theme=resolved_theme,
                design_system=design_system,
                default_styles=default_styles,
                build_dir=build_dir,
                production=production,
                root_path=root_path,
            )
            extensions = tuple(bootstrap_steps) if bootstrap_steps is not None else ()
            HedronBootstrapper(extension_steps=extensions).bootstrap(self, config)
            self.state.hedron_demand_driven_assets = demand_driven_assets
            self.add_middleware(
                RuntimeContextMiddleware,
                runtime=self._hedron_runtime,
            )

    @property
    def interactions(self) -> object:
        """Read-only interaction catalog for this application."""
        from hedron.interactions import app_interactions

        return app_interactions(self)

    def styles(
        self,
        name: str,
        source: str | Path,
        *,
        scope: str | None = None,
        layer: Literal["application", "overrides"] = "application",
        global_: bool = False,
        media: tuple[str, ...] = (),
        allowed_roots: Sequence[str | Path] | None = None,
    ) -> object:
        """Register one explicit local application stylesheet before the build seal."""
        with self._hedron_runtime.activate():
            from hedron.registration import fail_closed_late_registration
            from hedron_core.catalog import get_sealed_catalog
            from hedron_core.registry import register_application_style
            from hedron_core.registry.builder import active_builder

            fail_closed_late_registration(
                registry_sealed=active_builder().is_sealed,
                catalog_sealed=get_sealed_catalog() is not None,
                openapi_cached=cached_openapi(self) is not None,
            )
            meta = register_application_style(
                name=name,
                source=source,
                scope=scope,
                layer=layer,
                global_=global_,
                media=media,
                owner="application",
                provenance=f"{type(self).__module__}.{type(self).__name__}",
                allowed_roots=tuple(allowed_roots or (Path.cwd(),)),
            )
            existing = tuple(getattr(self.state, "hedron_application_styles", ()))
            self.state.hedron_application_styles = (*existing, meta.logical_id)
            return meta

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]
        from hedron.registration import fail_closed_late_registration
        from hedron_core.catalog import get_sealed_catalog
        from hedron_core.registry.builder import active_builder

        builder = active_builder()
        fail_closed_late_registration(
            registry_sealed=builder.is_sealed,
            catalog_sealed=get_sealed_catalog() is not None,
            openapi_cached=cached_openapi(self) is not None,
        )
        if isinstance(router, HedronRouter):
            router.attach_host_app(self)
        super().include_router(router, *args, **kwargs)
