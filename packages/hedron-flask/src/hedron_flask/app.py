"""Thin HedronFlask helper wrapping a native Flask application."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flask import Flask, Request, Response
from flask import session as flask_session

from hedron_core.adapter import FLASK_CAPABILITIES, AuthSignal
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderContext, RenderMode, RenderResult
from hedron_flask.blueprint import attach_hedron_to_flask
from hedron_flask.csrf import csrf_token_for_request, ensure_csrf_cookie, validate_csrf
from hedron_flask.htmx import htmx_context, render_mode_for_request
from hedron_flask.responses import component_response, interaction_response
from hedron_flask.routing import FlaskUrlReverser

__all__ = ["HedronFlask"]

_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


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
        **kwargs: Any,
    ) -> None:
        self.csrf_cookie_name = csrf_cookie_name
        self.csrf_protect = csrf_protect
        self._auto_csrf_cookie = auto_csrf_cookie
        self.flask: Flask | None = None
        self.url_reverser: FlaskUrlReverser | None = None
        if import_name is not None:
            app = Flask(import_name, **kwargs)
            self.init_app(app)

    def init_app(self, app: Flask) -> Flask:
        """Bind this extension to ``app`` (idempotent for the same app)."""
        existing = app.extensions.get("hedron")
        if existing is self:
            self.flask = app
            if self.url_reverser is None:
                self.url_reverser = FlaskUrlReverser(app)
            return app
        self.flask = app
        self.url_reverser = FlaskUrlReverser(app)
        attach_hedron_to_flask(app, self, auto_csrf_cookie=self._auto_csrf_cookie)
        return app

    @property
    def capabilities(self):
        return FLASK_CAPABILITIES

    def route(self, rule: str, **options: Any):
        if self.flask is None:
            raise RuntimeError("HedronFlask.init_app(app) must be called before route()")
        return self.flask.route(rule, **options)

    def page(self, rule: str, **options: Any):
        """Register a page view on the bound app (non-Blueprint convenience)."""
        from hedron_flask.blueprint import wrap_hedron_view

        methods = list(options.pop("methods", ("GET",)))
        require_csrf = any(m.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"} for m in methods)

        def decorator(view: Any) -> Any:
            if self.flask is None:
                raise RuntimeError("HedronFlask.init_app(app) must be called before page()")
            wrapped = wrap_hedron_view(view, require_csrf=require_csrf)
            self.flask.add_url_rule(rule, view_func=wrapped, methods=methods, **options)
            return view

        return decorator

    def component(self, rule: str, **options: Any):
        from hedron_flask.blueprint import wrap_hedron_view

        methods = list(options.pop("methods", ("GET",)))
        require_csrf = any(m.upper() not in {"GET", "HEAD", "OPTIONS", "TRACE"} for m in methods)

        def decorator(view: Any) -> Any:
            if self.flask is None:
                raise RuntimeError("HedronFlask.init_app(app) must be called before component()")
            wrapped = wrap_hedron_view(view, require_csrf=require_csrf)
            self.flask.add_url_rule(rule, view_func=wrapped, methods=methods, **options)
            return view

        return decorator

    def action(self, rule: str, **options: Any):
        from hedron_flask.blueprint import wrap_hedron_view

        methods = list(options.pop("methods", ("POST",)))

        def decorator(view: Any) -> Any:
            if self.flask is None:
                raise RuntimeError("HedronFlask.init_app(app) must be called before action()")
            wrapped = wrap_hedron_view(view, require_csrf=True)
            self.flask.add_url_rule(rule, view_func=wrapped, methods=methods, **options)
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
    ):
        if self.csrf_protect and request.method.upper() in _UNSAFE_METHODS:
            validate_csrf(request, cookie_name=self.csrf_cookie_name)
        if isinstance(value, InteractionResult):
            return interaction_response(
                value,
                context=context,
                mode=mode,
                extra_headers=extra_headers,
                headers_map=dict(request.headers),
                authenticated=self.auth_signal(request).authenticated,
            )
        return component_response(
            value,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
            headers_map=dict(request.headers),
            authenticated=self.auth_signal(request).authenticated,
        )

    def auth_signal(self, request: Request | None = None) -> AuthSignal:
        del request  # Flask session is the request-local proxy.
        user_id = flask_session.get("user_id")
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
        return csrf_token_for_request(request, cookie_name=self.csrf_cookie_name)

    def attach_csrf_cookie(
        self, response: Response, request: Request, token: str | None = None
    ) -> str:
        value = token or self.csrf_token(request)
        ensure_csrf_cookie(
            response,
            value,
            cookie_name=self.csrf_cookie_name,
            secure=request.is_secure,
        )
        return value

    def htmx(self, request: Request):
        return htmx_context(dict(request.headers))
