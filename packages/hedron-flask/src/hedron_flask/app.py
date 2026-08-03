"""Thin HedronFlask helper wrapping a native Flask application."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from flask import Flask, Request

from hedron_core.adapter import FLASK_CAPABILITIES, AuthSignal
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderContext, RenderMode, RenderResult
from hedron_flask.csrf import csrf_token_for_request, ensure_csrf_cookie
from hedron_flask.htmx import htmx_context, render_mode_for_request
from hedron_flask.responses import component_response, interaction_response
from hedron_flask.routing import FlaskUrlReverser

__all__ = ["HedronFlask"]


class HedronFlask:
    """Native Flask app with Hedron render and interaction helpers."""

    def __init__(
        self,
        import_name: str,
        *,
        csrf_cookie_name: str = "hedron_csrf",
        **kwargs: Any,
    ) -> None:
        self.flask = Flask(import_name, **kwargs)
        self.csrf_cookie_name = csrf_cookie_name
        self.url_reverser = FlaskUrlReverser(self.flask)

    @property
    def capabilities(self):
        return FLASK_CAPABILITIES

    def route(self, rule: str, **options: Any):
        return self.flask.route(rule, **options)

    def render(
        self,
        value: NodeLike | Component[Any] | RenderResult,
        request: Request,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> str:
        from hedron_flask.responses import _render_body

        result = _render_body(
            value,
            headers=request.headers,
            context=context,
            mode=mode or render_mode_for_request(request.headers),
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
        if isinstance(value, InteractionResult):
            return interaction_response(value, context=context, mode=mode)
        return component_response(
            value,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
        )

    def auth_signal(self, request: Request) -> AuthSignal:
        user_id = request.session.get("user_id") if request.session else None
        authenticated = bool(user_id)
        scopes = tuple(request.session.get("scopes", ())) if request.session else ()
        tenant_id = request.session.get("tenant_id") if request.session else None
        return AuthSignal(
            authenticated=authenticated,
            subject_id=str(user_id) if user_id is not None else None,
            scopes=scopes if isinstance(scopes, tuple) else tuple(scopes),
            tenant_id=str(tenant_id) if tenant_id is not None else None,
        )

    def csrf_token(self, request: Request) -> str:
        return csrf_token_for_request(request, cookie_name=self.csrf_cookie_name)

    def attach_csrf_cookie(self, response, request: Request, token: str | None = None):
        value = token or self.csrf_token(request)
        ensure_csrf_cookie(
            response,
            value,
            cookie_name=self.csrf_cookie_name,
            secure=request.is_secure,
        )
        return value

    def htmx(self, request: Request):
        return htmx_context(request.headers)
