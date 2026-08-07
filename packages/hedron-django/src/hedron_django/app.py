"""Thin HedronDjango helper for native Django views."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.adapter import DJANGO_CAPABILITIES, AuthSignal
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.rendering import RenderContext, RenderMode, RenderResult
from hedron_django.csrf import csrf_token_for_request
from hedron_django.htmx import htmx_context, render_mode_for_request
from hedron_django.responses import _headers_mapping, component_response, interaction_response
from hedron_django.routing import DjangoUrlReverser

__all__ = ["HedronDjango"]


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
            mode=mode or render_mode_for_request(_headers_mapping(request)),
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
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
    ) -> HttpResponse:
        from hedron_django.csrf import seed_csrf_cookie

        if (request.method or "GET").upper() in {"GET", "HEAD"}:
            seed_csrf_cookie(request)
        if isinstance(value, InteractionResult):
            return interaction_response(
                value,
                request=request,
                context=context,
                mode=mode,
                extra_headers=extra_headers,
                authenticated=self.auth_signal(request).authenticated,
                fragment_regions=fragment_regions,
            )
        return component_response(
            value,
            request=request,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
            authenticated=self.auth_signal(request).authenticated,
            fragment_regions=fragment_regions,
        )

    def auth_signal(self, request: HttpRequest) -> AuthSignal:
        user = getattr(request, "user", None)
        authenticated = bool(getattr(user, "is_authenticated", False))
        pk = getattr(user, "pk", None)
        subject_id = str(pk) if authenticated and pk is not None else None
        scopes: tuple[str, ...] = ()
        session = getattr(request, "session", None)
        tenant_id = session.get("tenant_id") if session is not None else None
        return AuthSignal(
            authenticated=authenticated,
            subject_id=subject_id,
            scopes=scopes,
            tenant_id=str(tenant_id) if tenant_id is not None else None,
        )

    def csrf_token(self, request: HttpRequest) -> str:
        return csrf_token_for_request(request)

    def htmx(self, request: HttpRequest):
        return htmx_context(_headers_mapping(request))
