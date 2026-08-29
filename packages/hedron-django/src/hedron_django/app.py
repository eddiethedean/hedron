"""Thin HedronDjango helper for native Django views."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from django.http import HttpRequest, HttpResponse

from hedron_core.adapter import DJANGO_CAPABILITIES, AuthSignal, CapabilityRecord
from hedron_core.component import Component, NodeLike
from hedron_core.htmx_contract import HtmxContext
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.interaction_067 import Outcome
from hedron_core.rendering import RenderContext, RenderMode, RenderResult
from hedron_django.csrf import csrf_token_for_request
from hedron_django.htmx import htmx_context, render_mode_for_request
from hedron_django.responses import (
    _headers_mapping,
    _outcome_response,
    component_response,
    interaction_response,
)
from hedron_django.routing import HEDRON_APP_ID, DjangoUrlReverser

__all__ = ["HedronDjango"]


class HedronDjango:
    """Native Django integration with Hedron render and interaction helpers."""

    def __init__(self) -> None:
        from hedron_django.apps import run_django_production_gates

        self.url_reverser = DjangoUrlReverser()
        self.hedron_app_id = HEDRON_APP_ID
        run_django_production_gates()

    @property
    def capabilities(self) -> CapabilityRecord:
        """Return the immutable capability declaration for the Django adapter."""
        return DJANGO_CAPABILITIES

    def render(
        self,
        value: NodeLike | Component[Any] | RenderResult,
        request: HttpRequest,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
    ) -> str:
        """Render a Hedron value to HTML using request-derived render mode."""
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
        allow_undeclared_targets: bool = False,
    ) -> HttpResponse:
        """Render a Hedron value as a synchronous Django response.

        Raises:
            RuntimeError: If called from a running event loop. ASGI views must
                await :meth:`respond_async` so component preparation is not lost.
        """
        from hedron_core.async_bridge import running_loop
        from hedron_django.csrf import DjangoCsrfError, seed_csrf_cookie, validate_csrf

        if running_loop():
            raise RuntimeError(
                "HedronDjango.respond() cannot prepare components while an event loop "
                "is running; await respond_async(...) from ASGI views instead."
            )
        method = (request.method or "GET").upper()
        if method in {"GET", "HEAD"}:
            seed_csrf_cookie(request)
        else:
            try:
                validate_csrf(request)
            except DjangoCsrfError as exc:
                return HttpResponse(
                    str(exc).encode("utf-8"),
                    status=403,
                    content_type="text/plain; charset=utf-8",
                )
        from hedron_core.diagnostics import HedronError
        from hedron_core.updates import compile_to_interaction

        try:
            compiled = compile_to_interaction(value, expected_app_id=self.hedron_app_id)
        except HedronError as exc:
            code = getattr(exc.diagnostic, "code", "")
            status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
            return HttpResponse(str(exc).encode("utf-8"), status=status, content_type="text/plain")
        if isinstance(compiled, InteractionResult):
            value = compiled
        if isinstance(compiled, Outcome):
            return _outcome_response(
                compiled,
                request=request,
                authenticated=self.auth_signal(request).authenticated,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                app_id=self.hedron_app_id,
            )
        if isinstance(value, InteractionResult):
            return interaction_response(
                value,
                request=request,
                context=context,
                mode=mode,
                extra_headers=extra_headers,
                authenticated=self.auth_signal(request).authenticated,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
        return component_response(
            value,
            request=request,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
            authenticated=self.auth_signal(request).authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )

    async def respond_async(
        self,
        value: NodeLike | Component[Any] | InteractionResult | RenderResult,
        request: HttpRequest,
        *,
        context: RenderContext | None = None,
        mode: RenderMode | None = None,
        extra_headers: Mapping[str, str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
    ) -> HttpResponse:
        """ASGI-safe respond that awaits ``prepare_tree`` before rendering."""
        from hedron_core.prepare import prepare_tree
        from hedron_django.csrf import DjangoCsrfError, seed_csrf_cookie, validate_csrf

        method = (request.method or "GET").upper()
        if method in {"GET", "HEAD"}:
            seed_csrf_cookie(request)
        else:
            try:
                validate_csrf(request)
            except DjangoCsrfError as exc:
                return HttpResponse(
                    str(exc).encode("utf-8"),
                    status=403,
                    content_type="text/plain; charset=utf-8",
                )

        from hedron_core.diagnostics import HedronError
        from hedron_core.updates import compile_to_interaction

        try:
            compiled = compile_to_interaction(value, expected_app_id=self.hedron_app_id)
        except HedronError as exc:
            code = getattr(exc.diagnostic, "code", "")
            status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
            return HttpResponse(str(exc).encode("utf-8"), status=status, content_type="text/plain")
        if isinstance(compiled, InteractionResult):
            value = compiled
        if isinstance(compiled, Outcome):
            return _outcome_response(
                compiled,
                request=request,
                authenticated=self.auth_signal(request).authenticated,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                app_id=self.hedron_app_id,
            )
        if isinstance(value, InteractionResult):
            if value.content is not None:
                await prepare_tree(value.content)
            for update in value.oob:
                await prepare_tree(update.content)
            return interaction_response(
                value,
                request=request,
                context=context,
                mode=mode,
                extra_headers=extra_headers,
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
            request=request,
            context=context,
            mode=mode,
            extra_headers=extra_headers,
            authenticated=self.auth_signal(request).authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            skip_prepare=True,
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

    def htmx(self, request: HttpRequest) -> HtmxContext:
        """Parse the request's approved HTMX headers into a typed context."""
        return htmx_context(_headers_mapping(request))
