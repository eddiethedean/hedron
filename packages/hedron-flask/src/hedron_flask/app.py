"""Thin HedronFlask helper wrapping a native Flask application."""

from __future__ import annotations

import logging
import secrets
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from typing import Any, ParamSpec, TypeVar, cast

from flask import Flask, Request, Response
from flask import session as flask_session
from flask.typing import RouteCallable

from hedron_core.adapter import FLASK_CAPABILITIES, AuthSignal
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.rendering import RenderContext, RenderMode, RenderResult
from hedron_core.security_policy import SecurityPolicy, SecurityProfileName
from hedron_flask.blueprint import attach_hedron_to_flask
from hedron_flask.csrf import (
    csrf_cookie_force_secure,
    csrf_cookie_should_be_secure,
    csrf_token_for_request,
    ensure_csrf_cookie,
    validate_csrf,
)
from hedron_flask.htmx import htmx_context, render_mode_for_request
from hedron_flask.responses import component_response, interaction_response
from hedron_flask.routing import FlaskUrlReverser
from hedron_flask.static_mount import mount_hedron_static

__all__ = ["HedronFlask"]

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
P = ParamSpec("P")
R = TypeVar("R")
_logger = logging.getLogger("hedron.flask")


class HedronFlask:
    """Native Flask extension with Hedron render and interaction helpers.

    Construct with an ``import_name`` to own a Flask app (legacy), or construct
    without an app and call :meth:`init_app` for application-factory composition.
    """

    def __init__(
        self,
        import_name: str | None = None,
        *,
        csrf_cookie_name: str = "hedron_csrf",
        auto_csrf_cookie: bool = True,
        csrf_protect: bool = True,
        csrf_cookie_secure: bool | None = None,
        security: SecurityProfileName | str | SecurityPolicy = "standard",
        **kwargs: Any,
    ) -> None:
        self.csrf_cookie_name = csrf_cookie_name
        self.csrf_protect = csrf_protect
        # True: always Secure (FastAPI STRICT parity). None: request.is_secure
        # or FLASK_ENV/ENV=production. False: never Secure.
        self.csrf_cookie_secure = csrf_cookie_secure
        self._auto_csrf_cookie = auto_csrf_cookie
        self.security_policy = SecurityPolicy.from_name(security)
        self._sync_csrf_cookie_name()
        self.hedron_app_id = secrets.token_hex(8)
        self.flask: Flask | None = None
        self.url_reverser: FlaskUrlReverser | None = None
        if import_name is not None:
            app = Flask(import_name, **kwargs)
            self.init_app(app)

    def _sync_csrf_cookie_name(self) -> None:
        """Keep extension and SecurityPolicy CSRF cookie names identical."""
        policy = self.security_policy
        strategy = policy.resolve_csrf_strategy() if policy.csrf_enabled else None
        strategy_name = getattr(strategy, "cookie_name", None) if strategy is not None else None
        if (
            self.csrf_cookie_name != "hedron_csrf"
            and policy.csrf is None
            and policy.csrf_cookie_name == "hedron_csrf"
        ):
            # Explicit extension override wins over the default policy name.
            self.security_policy = replace(policy, csrf_cookie_name=self.csrf_cookie_name)
            return
        if isinstance(strategy_name, str) and strategy_name:
            self.csrf_cookie_name = strategy_name
            if policy.csrf is None and policy.csrf_cookie_name != strategy_name:
                self.security_policy = replace(policy, csrf_cookie_name=strategy_name)

    def init_app(
        self,
        app: Flask,
        *,
        security: SecurityProfileName | str | SecurityPolicy | None = None,
    ) -> Flask:
        """Bind this extension to ``app`` (idempotent for the same app)."""
        if security is not None:
            self.security_policy = SecurityPolicy.from_name(security)
        self._sync_csrf_cookie_name()
        existing = app.extensions.get("hedron")
        if existing is self:
            self.flask = app
            if self.url_reverser is None:
                self.url_reverser = FlaskUrlReverser(app)
            return app
        self.flask = app
        self.url_reverser = FlaskUrlReverser(app)
        attach_hedron_to_flask(
            app,
            self,
            auto_csrf_cookie=self._auto_csrf_cookie,
            security=self.security_policy,
        )
        mount_hedron_static(app)
        return app

    @property
    def capabilities(self):
        return FLASK_CAPABILITIES

    def route(self, rule: str, **options: Any):
        if self.flask is None:
            raise RuntimeError("HedronFlask.init_app(app) must be called before route()")
        return self.flask.route(rule, **options)

    def page(self, rule: str, **options: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Register a page view on the bound app (non-Blueprint convenience)."""
        from hedron_flask.blueprint import wrap_hedron_view

        methods = list(options.pop("methods", ("GET",)))
        fragment_regions = options.pop("fragment_regions", None)
        allow_undeclared_targets = bool(options.pop("allow_undeclared_targets", False))
        require_csrf = any(m.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"} for m in methods)

        def decorator(view: Callable[P, R]) -> Callable[P, R]:
            if self.flask is None:
                raise RuntimeError("HedronFlask.init_app(app) must be called before page()")
            wrapped = wrap_hedron_view(
                view,
                require_csrf=require_csrf,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.flask.add_url_rule(
                rule, view_func=cast(RouteCallable, wrapped), methods=methods, **options
            )
            return view

        return decorator

    def component(self, rule: str, **options: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
        from hedron_flask.blueprint import wrap_hedron_view

        methods = list(options.pop("methods", ("GET",)))
        fragment_regions = options.pop("fragment_regions", None)
        allow_undeclared_targets = bool(options.pop("allow_undeclared_targets", False))
        require_csrf = any(m.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"} for m in methods)

        def decorator(view: Callable[P, R]) -> Callable[P, R]:
            if self.flask is None:
                raise RuntimeError("HedronFlask.init_app(app) must be called before component()")
            wrapped = wrap_hedron_view(
                view,
                require_csrf=require_csrf,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.flask.add_url_rule(
                rule, view_func=cast(RouteCallable, wrapped), methods=methods, **options
            )
            return view

        return decorator

    def action(self, rule: str, **options: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
        from hedron_flask.blueprint import wrap_hedron_view

        methods = list(options.pop("methods", ("POST",)))
        fragment_regions = options.pop("fragment_regions", None)
        allow_undeclared_targets = bool(options.pop("allow_undeclared_targets", False))

        def decorator(view: Callable[P, R]) -> Callable[P, R]:
            if self.flask is None:
                raise RuntimeError("HedronFlask.init_app(app) must be called before action()")
            wrapped = wrap_hedron_view(
                view,
                require_csrf=True,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.flask.add_url_rule(
                rule, view_func=cast(RouteCallable, wrapped), methods=methods, **options
            )
            return view

        return decorator

    def render(
        self,
        value: NodeLike | Component[Any] | RenderResult,
        request: Request,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> str:
        from hedron_flask.responses import _render_body

        headers = dict(request.headers)
        result = _render_body(
            value,
            headers=headers,
            context=context,
            mode=mode or render_mode_for_request(headers),
        )
        return result.html

    def respond(
        self,
        value: NodeLike | Component[Any] | InteractionResult | RenderResult,
        request: Request,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
        extra_headers: Mapping[str, str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
    ):
        from hedron_core.async_bridge import running_loop

        if running_loop():
            raise RuntimeError(
                "HedronFlask.respond() cannot prepare components while an event loop "
                "is running; await respond_async(...) instead."
            )
        if (
            self.csrf_protect
            and self.security_policy.csrf_enabled
            and request.method.upper() not in _SAFE_METHODS
        ):
            validate_csrf(
                request,
                cookie_name=self.csrf_cookie_name,
                policy=self.security_policy,
            )
        from hedron_core.diagnostics import HedronError
        from hedron_core.updates import compile_to_interaction

        try:
            compiled = compile_to_interaction(value, expected_app_id=self.hedron_app_id)
        except HedronError as exc:
            code = getattr(exc.diagnostic, "code", "")
            status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
            from flask import Response as FlaskResponse

            return FlaskResponse(str(exc), status=status, content_type="text/plain")
        if isinstance(compiled, InteractionResult):
            value = compiled
        if isinstance(value, InteractionResult):
            return interaction_response(
                value,
                context=context,
                mode=mode,
                extra_headers=extra_headers,
                headers_map=dict(request.headers),
                authenticated=self.auth_signal(request).authenticated,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
        return component_response(
            value,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
            headers_map=dict(request.headers),
            authenticated=self.auth_signal(request).authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )

    async def respond_async(
        self,
        value: NodeLike | Component[Any] | InteractionResult | RenderResult,
        request: Request,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
        extra_headers: Mapping[str, str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
    ):
        """Async-safe respond that awaits ``prepare_tree`` before rendering."""
        from hedron_core.prepare import prepare_tree

        if (
            self.csrf_protect
            and self.security_policy.csrf_enabled
            and request.method.upper() not in _SAFE_METHODS
        ):
            validate_csrf(
                request,
                cookie_name=self.csrf_cookie_name,
                policy=self.security_policy,
            )
        from hedron_core.diagnostics import HedronError
        from hedron_core.updates import compile_to_interaction

        try:
            compiled = compile_to_interaction(value, expected_app_id=self.hedron_app_id)
        except HedronError as exc:
            code = getattr(exc.diagnostic, "code", "")
            status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
            from flask import Response as FlaskResponse

            return FlaskResponse(str(exc), status=status, content_type="text/plain")
        if isinstance(compiled, InteractionResult):
            value = compiled
        if isinstance(value, InteractionResult):
            if value.content is not None:
                await prepare_tree(value.content)
            for update in value.oob:
                await prepare_tree(update.content)
            return interaction_response(
                value,
                context=context,
                mode=mode,
                extra_headers=extra_headers,
                headers_map=dict(request.headers),
                authenticated=self.auth_signal(request).authenticated,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                skip_prepare=True,
            )
        if (
            isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__")
        ) and not isinstance(value, RenderResult):
            await prepare_tree(value)  # type: ignore[arg-type]
        return component_response(
            value,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
            headers_map=dict(request.headers),
            authenticated=self.auth_signal(request).authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            skip_prepare=True,
        )

    def auth_signal(self, request: Request | None = None) -> AuthSignal:
        del request  # Flask session / flask_login proxies are request-local.
        user_id = None
        try:
            from flask_login import current_user  # type: ignore[import-not-found]

            if getattr(current_user, "is_authenticated", False):
                get_id = getattr(current_user, "get_id", None)
                if callable(get_id):
                    user_id = get_id()
                if user_id is None:
                    user_id = getattr(current_user, "id", None)
        except ImportError:
            _logger.debug("flask_login is not installed; using session identity")
        except Exception as exc:  # noqa: BLE001
            # flask_login may raise outside a request context; fall back to session.
            _logger.debug("flask_login current_user unavailable: %s", exc)
        if user_id is None:
            user_id = flask_session.get("user_id")
            if user_id is None:
                user_id = flask_session.get("_user_id")
        authenticated = bool(user_id)
        scopes_raw = flask_session.get("scopes", ())
        scopes = tuple(scopes_raw) if isinstance(scopes_raw, (list, tuple)) else ()
        tenant_id = flask_session.get("tenant_id")
        return AuthSignal(
            authenticated=authenticated,
            subject_id=str(user_id) if user_id is not None else None,
            scopes=scopes,
            tenant_id=str(tenant_id) if tenant_id is not None else None,
        )

    def csrf_token(self, request: Request) -> str:
        return csrf_token_for_request(
            request,
            cookie_name=self.csrf_cookie_name,
            policy=self.security_policy,
        )

    def attach_csrf_cookie(
        self, response: Response, request: Request, token: str | None = None
    ) -> str:
        if not self.security_policy.csrf_enabled:
            return ""
        value = token or self.csrf_token(request)
        from hedron_core.mount import cookie_path_for_mount

        script_root = getattr(request, "script_root", "") or ""
        cookie_path = (
            cookie_path_for_mount(script_root)
            if isinstance(script_root, str) and script_root
            else "/"
        )
        configured = getattr(self, "csrf_cookie_path", None)
        if isinstance(configured, str) and configured:
            cookie_path = configured
        ensure_csrf_cookie(
            response,
            value,
            cookie_name=self.csrf_cookie_name,
            secure=csrf_cookie_should_be_secure(
                request,
                force_secure=csrf_cookie_force_secure(
                    self.csrf_cookie_secure, self.security_policy
                ),
            ),
            path=cookie_path,
        )
        return value

    def htmx(self, request: Request):
        return htmx_context(dict(request.headers))
