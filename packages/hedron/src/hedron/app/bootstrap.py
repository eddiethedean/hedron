"""Composable application bootstrap steps for the Hedron FastAPI host.

The public :class:`hedron.Hedron` object remains the framework façade.  This
module owns construction-time wiring so policy resolution, mount handling,
middleware installation, and optional integrations can evolve independently.
"""

from __future__ import annotations

import logging
import secrets
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, TypeGuard, cast

from fastapi import FastAPI
from fastapi.params import Depends as DependsParam

from hedron.app.explorer import (
    ExplorerMode,
    install_explorer_bridges,
    mount_explorer_if_enabled,
    resolve_explorer_mode,
)
from hedron.app.sessions import SessionHost, configure_sessions
from hedron.openapi import install_openapi
from hedron.routing.router import HedronRouter
from hedron.security.headers import SecurityHeadersMiddleware
from hedron.security.plane_middleware import SecurityPlaneMiddleware
from hedron.security.policy import SecurityPolicy, SecurityProfile, SecurityProfileName
from hedron.static_mount import mount_build_assets, mount_hedron_static
from hedron_core import production_gate
from hedron_core.compile_gate import is_production_env
from hedron_core.design_system import DesignSystem
from hedron_core.theme import Theme, ensure_default_theme_registered, register_theme_instance

logger = logging.getLogger("hedron")
_HEDRON_CONSTRUCTOR_WARNING_STACKLEVEL = 5

__all__ = [
    "HedronBootstrapConfig",
    "HedronBootstrapContext",
    "HedronBootstrapStep",
    "HedronBootstrapper",
    "normalize_theme_selection",
]


def _is_theme(value: object) -> TypeGuard[Theme]:
    return isinstance(value, Theme)


def normalize_theme_selection(
    theme: str | Theme | DesignSystem | None,
) -> tuple[str | None, DesignSystem | None]:
    """Convert a theme input into a registered name and optional design system."""
    if theme is None:
        return None, None
    if isinstance(theme, str):
        return theme, None
    from hedron_core.registry import get_registry

    design: DesignSystem | None = None
    if isinstance(theme, DesignSystem):
        design = theme
        theme_obj = theme.to_theme()
    elif _is_theme(theme):
        theme_obj = theme
    else:
        raise TypeError(
            f"theme must be str | Theme | DesignSystem | None; got {type(theme).__name__}"
        )
    if get_registry().get_theme(theme_obj.name) is None:
        register_theme_instance(theme_obj)
    return theme_obj.name, design


@dataclass(frozen=True)
class HedronBootstrapConfig:
    """Immutable inputs shared by all application setup steps."""

    security: SecurityProfileName | str | SecurityPolicy
    explorer: ExplorerMode | str | None
    session_secret: str | None
    enable_sessions: bool
    explorer_dependencies: tuple[DependsParam, ...]
    theme: str | None
    design_system: DesignSystem | None
    default_styles: bool
    build_dir: str | Path | None
    production: bool | None
    root_path: str | None


@dataclass
class HedronBootstrapContext:
    """Mutable results produced by setup steps and consumed by later steps."""

    config: HedronBootstrapConfig
    policy: SecurityPolicy | None = None
    is_production: bool = False
    requested_explorer_mode: str = "off"
    explorer_mode: str = "off"
    mount_cookie_path: str = "/"
    mount_was_configured: bool = False


class HedronBootstrapStep(Protocol):
    """One independently testable application construction responsibility."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None: ...


class IdentityStep:
    """Assign a process-local application identity before route registration."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        del context
        app.hedron_app_id = secrets.token_hex(8)  # type: ignore[attr-defined]
        app.state.hedron_app_id = app.hedron_app_id  # type: ignore[attr-defined]


class ThemeStep:
    """Publish the resolved theme contract to the app and request state."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        config = context.config
        ensure_default_theme_registered()
        app.hedron_theme = config.theme  # type: ignore[attr-defined]
        app.hedron_design_system = config.design_system  # type: ignore[attr-defined]
        app.hedron_default_styles = config.default_styles  # type: ignore[attr-defined]
        app.state.hedron_theme = config.theme
        app.state.hedron_design_system = config.design_system
        app.state.hedron_default_styles = config.default_styles


class SecurityStep:
    """Resolve security and production gates without installing middleware."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        config = context.config
        policy = SecurityPolicy.from_name(config.security)
        is_prod = is_production_env(production=config.production)
        requested_mode = resolve_explorer_mode(
            config.explorer,
            explorer_enabled=policy.explorer_enabled,
            is_prod=False,
            warning_stacklevel=_HEDRON_CONSTRUCTOR_WARNING_STACKLEVEL,
        )
        context.policy = policy
        context.is_production = is_prod
        context.requested_explorer_mode = requested_mode
        context.explorer_mode = resolve_explorer_mode(
            config.explorer,
            explorer_enabled=policy.explorer_enabled,
            is_prod=is_prod,
            warning_stacklevel=_HEDRON_CONSTRUCTOR_WARNING_STACKLEVEL,
        )
        app.hedron_policy = policy  # type: ignore[attr-defined]
        app.hedron_explorer_mode = context.explorer_mode  # type: ignore[attr-defined]
        app.state.hedron_security = policy
        app.state.hedron_production = (
            config.production if config.production is not None else is_prod
        )
        production_gate.assert_durable_backends(
            production=is_prod,
            strict_profile=policy.profile is SecurityProfile.STRICT,
            warning_stacklevel=_HEDRON_CONSTRUCTOR_WARNING_STACKLEVEL,
        )
        production_gate.assert_production_security_config(
            production=is_prod,
            security_profile=policy.profile.value,
            session_secret=config.session_secret,
            sessions_enabled=config.enable_sessions,
            explorer_mode=requested_mode,
            allow_external_redirects=policy.allow_external_redirects,
            content_security_policy=policy.content_security_policy,
        )


class MountStep:
    """Resolve mount and cookie paths before session middleware is installed."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        config = context.config
        try:
            from hedron.mount import normalize_mount_path, resolve_mount_path_from_environ

            if config.root_path is not None:
                context.mount_was_configured = True
                explicit = normalize_mount_path(config.root_path)
                context.mount_cookie_path = explicit if explicit else "/"
                app.state.hedron_mount_path = explicit
            else:
                env_mount = resolve_mount_path_from_environ()
                if env_mount is not None:
                    context.mount_was_configured = True
                    context.mount_cookie_path = env_mount.cookie_path
                    app.state.hedron_mount_path = env_mount.path
                else:
                    app.state.hedron_mount_path = ""
        except (ImportError, OSError, ValueError, TypeError) as exc:
            logger.debug("Mount path from environ unavailable: %s", exc)
            app.state.hedron_mount_path = ""
        app.state.hedron_mount_was_configured = context.mount_was_configured


class SessionStep:
    """Install session middleware according to resolved policy and mount state."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        config = context.config
        configure_sessions(
            cast(SessionHost, app),
            session_secret=config.session_secret,
            enable_sessions=config.enable_sessions,
            is_prod=context.is_production,
            mount_cookie_path=context.mount_cookie_path,
            warning_stacklevel=_HEDRON_CONSTRUCTOR_WARNING_STACKLEVEL,
        )


class MiddlewareStep:
    """Install the framework security middleware stack."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        assert context.policy is not None
        app.add_middleware(SecurityHeadersMiddleware, policy=context.policy)
        app.add_middleware(
            SecurityPlaneMiddleware,
            policy=context.policy,
            application_id=getattr(app.state, "hedron_app_id", "hedron"),
        )


class AssetMountStep:
    """Mount bundled and precompiled application assets."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        mount_hedron_static(app)
        mount_build_assets(app, context.config.build_dir)


class RoutingStep:
    """Create the root Hedron router and bind it to the host application."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        del context

        root_router = HedronRouter()
        root_router.attach_host_app(app)
        app._root_router = root_router  # type: ignore[attr-defined]


class OpenApiStep:
    """Install Hedron's OpenAPI projection."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        del context
        install_openapi(app)


class ResponseHandlerStep:
    """Install canonical interaction response handlers."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        del context

        from hedron.status_responses import install_interaction_handlers

        install_interaction_handlers(app)


class ExplorerStep:
    """Install Explorer bridges and mount the selected Explorer surface."""

    def apply(self, app: FastAPI, context: HedronBootstrapContext) -> None:
        install_explorer_bridges(app)
        mount_explorer_if_enabled(
            app,
            explorer_mode=context.explorer_mode,
            explorer_dependencies=context.config.explorer_dependencies,
        )


class HedronBootstrapper:
    """Run mandatory setup followed by optional application extension steps."""

    def __init__(self, extension_steps: Sequence[HedronBootstrapStep] = ()) -> None:
        self.core_steps: tuple[HedronBootstrapStep, ...] = (
            IdentityStep(),
            ThemeStep(),
            SecurityStep(),
            MountStep(),
            SessionStep(),
            MiddlewareStep(),
            AssetMountStep(),
            RoutingStep(),
            OpenApiStep(),
            ResponseHandlerStep(),
            ExplorerStep(),
        )
        self.extension_steps = tuple(extension_steps)

    @property
    def steps(self) -> tuple[HedronBootstrapStep, ...]:
        return (*self.core_steps, *self.extension_steps)

    def bootstrap(self, app: FastAPI, config: HedronBootstrapConfig) -> HedronBootstrapContext:
        context = HedronBootstrapContext(config=config)
        for step in self.steps:
            step.apply(app, context)
        self._validate_invariants(app, context)
        app._hedron_bootstrap_context = context  # type: ignore[attr-defined]
        return context

    @staticmethod
    def _validate_invariants(app: FastAPI, context: HedronBootstrapContext) -> None:
        missing = [
            name
            for name in ("hedron_app_id", "hedron_policy", "hedron_explorer_mode", "_root_router")
            if not hasattr(app, name)
        ]
        middleware_types = {middleware.cls for middleware in app.user_middleware}
        if SecurityHeadersMiddleware not in middleware_types:
            missing.append("SecurityHeadersMiddleware")
        if SecurityPlaneMiddleware not in middleware_types:
            missing.append("SecurityPlaneMiddleware")
        if (
            context.policy is None
            or getattr(app.state, "hedron_security", None) is not context.policy
        ):
            missing.append("hedron_security")
        if missing:
            names = ", ".join(sorted(set(missing)))
            raise RuntimeError(f"Hedron bootstrap invariants were not satisfied: {names}")
