"""HedronRoute — APIRoute subclass with component return handling."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request
from fastapi.routing import APIRoute
from starlette.responses import Response as StarletteResponse

from hedron.async_utils import await_if_needed
from hedron.context import render_context_from_request
from hedron.responses import HTML, render_component_response
from hedron.security.csrf import ensure_csrf_cookie
from hedron.security.policy import SecurityPolicy
from hedron_core.component import Component
from hedron_core.models import Model
from hedron_core.rendering import RenderMode

__all__ = ["HedronRoute"]


class HedronRoute(APIRoute):
    """APIRoute that converts component returns into HTML responses."""

    hedron_kind: str | None = None

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, StarletteResponse]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> StarletteResponse:
            from hedron.routing.router import current_request

            policy: SecurityPolicy = getattr(
                request.app.state, "hedron_security", SecurityPolicy.from_name("standard")
            )
            token = current_request.set(request)
            try:
                response = await original(request)
            finally:
                current_request.reset(token)

            if isinstance(response, StarletteResponse):
                if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                    ensure_csrf_cookie(response, policy)
                return response
            return response

        return handler

    @staticmethod
    async def convert_endpoint_result(
        request: Request,
        result: Any,
        *,
        mode: RenderMode | None = None,
        kind: str = "page",
    ) -> StarletteResponse:
        policy: SecurityPolicy = getattr(
            request.app.state, "hedron_security", SecurityPolicy.from_name("standard")
        )
        authenticated = bool(getattr(request.state, "hedron_authenticated", False))
        result = await await_if_needed(result)

        if isinstance(result, StarletteResponse):
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(result, policy)
            return result
        if isinstance(result, HTML):
            response = render_component_response(
                result,
                request=request,
                context=render_context_from_request(request),
                policy=policy,
                authenticated=authenticated,
            )
            if policy.csrf_enabled:
                ensure_csrf_cookie(response, policy)
            return response
        if isinstance(result, Model) and not isinstance(result, Component):
            from fastapi.encoders import jsonable_encoder
            from fastapi.responses import JSONResponse

            return JSONResponse(jsonable_encoder(result))
        if isinstance(result, Component) or hasattr(result, "render"):
            force = mode
            if kind == "component":
                force = force or RenderMode.FRAGMENT
            response = render_component_response(
                result,  # type: ignore[arg-type]
                request=request,
                context=render_context_from_request(request),
                mode=force,
                policy=policy,
                authenticated=authenticated,
            )
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(response, policy)
            return response
        # Sequences/strings and other NodeLike values render as fragments/pages.
        if isinstance(result, (str, int, float, bool, list, tuple)) or result is None:
            force = mode
            if kind == "component":
                force = force or RenderMode.FRAGMENT
            response = render_component_response(
                result,  # type: ignore[arg-type]
                request=request,
                context=render_context_from_request(request),
                mode=force,
                policy=policy,
                authenticated=authenticated,
            )
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(response, policy)
            return response
        return result  # type: ignore[no-any-return]
