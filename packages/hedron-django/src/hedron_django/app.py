"""Thin HedronDjango helper for native Django views."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.adapter import DJANGO_CAPABILITIES, AuthSignal
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderContext, RenderMode, RenderResult
from hedron_django.csrf import csrf_token_for_request
from hedron_django.htmx import htmx_context, render_mode_for_request
from hedron_django.responses import component_response, interaction_response
from hedron_django.routing import DjangoUrlReverser

__all__ = ["HedronDjango", "QUERYSET_DATASOURCE_DEFERRED"]


# Explicit deferral per D-036 — QuerySet DataSource is not implemented in phase 0.7.
QUERYSET_DATASOURCE_DEFERRED = True


class HedronDjango:
    """Native Django integration with Hedron render and interaction helpers."""

    def __init__(self) -> None:
        self.url_reverser = DjangoUrlReverser()

    @property
    def capabilities(self):
        return DJANGO_CAPABILITIES

    def render(
        self,
        value: NodeLike | Component[Any] | RenderResult,
        request: HttpRequest,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> str:
        from hedron_django.responses import _render_body

        result = _render_body(
            value,
            request=request,
            context=context,
            mode=mode or render_mode_for_request(dict(request.headers)),
        )
        return result.html

    def respond(
        self,
        value: NodeLike | Component[Any] | InteractionResult | RenderResult,
        request: HttpRequest,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        if isinstance(value, InteractionResult):
            return interaction_response(value, request=request, context=context, mode=mode)
        return component_response(
            value,
            request=request,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
        )

    def auth_signal(self, request: HttpRequest) -> AuthSignal:
        user = getattr(request, "user", None)
        authenticated = bool(getattr(user, "is_authenticated", False))
        pk = getattr(user, "pk", None)
        subject_id = str(pk) if authenticated and pk is not None else None
        scopes: tuple[str, ...] = ()
        tenant_id = request.session.get("tenant_id") if hasattr(request, "session") else None
        return AuthSignal(
            authenticated=authenticated,
            subject_id=subject_id,
            scopes=scopes,
            tenant_id=str(tenant_id) if tenant_id is not None else None,
        )

    def csrf_token(self, request: HttpRequest) -> str:
        return csrf_token_for_request(request)

    def htmx(self, request: HttpRequest):
        return htmx_context(dict(request.headers))
