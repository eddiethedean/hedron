"""HedronRoute — APIRoute subclass with component return handling."""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any

from fastapi import Request
from fastapi.routing import APIRoute
from starlette.responses import Response as StarletteResponse

from hedron.async_utils import await_if_needed
from hedron.context import render_context_from_request
from hedron.interaction import InteractionResult, interaction_headers, resolve_fragment_region
from hedron.responses import HTML, render_component_response
from hedron.security.csrf import ensure_csrf_cookie
from hedron.security.policy import SecurityPolicy
from hedron_core.builtins import Fragment
from hedron_core.component import Component
from hedron_core.models import Model
from hedron_core.rendering import RenderMode

__all__ = ["HedronRoute"]


def _is_hedron_value(value: Any) -> bool:
    if isinstance(value, (HTML, Component, StarletteResponse, InteractionResult)):
        return True
    if isinstance(value, Model) and not isinstance(value, Component):
        return True
    return callable(getattr(value, "render", None))


class HedronRoute(APIRoute):
    """APIRoute that converts component returns into HTML responses."""

    hedron_kind: str | None = None

    def __init__(self, path: str, endpoint: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        # Convert HTML/Component returns before FastAPI serializes them.
        if not getattr(endpoint, "_hedron_plain_wrapped", False):
            endpoint = self._wrap_plain_endpoint(endpoint)
        super().__init__(path, endpoint, *args, **kwargs)

    @classmethod
    def _wrap_plain_endpoint(cls, endpoint: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(endpoint)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            from hedron.routing.router import current_request

            result = endpoint(*args, **kwargs)
            result = await await_if_needed(result)
            if isinstance(result, StarletteResponse) or not _is_hedron_value(result):
                return result
            request = current_request.get()
            if request is None:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
                maybe = kwargs.get("request")
                if isinstance(maybe, Request):
                    request = maybe
            if request is None:
                raise RuntimeError("Hedron HTML/Component returns require an active Request")
            kind = "page"
            return await cls.convert_endpoint_result(request, result, mode=None, kind=kind)

        wrapped._hedron_plain_wrapped = True  # type: ignore[attr-defined]
        # Preserve signature for FastAPI dependency injection.
        import contextlib

        with contextlib.suppress(TypeError, ValueError):
            wrapped.__signature__ = inspect.signature(endpoint)  # type: ignore[attr-defined]
        return wrapped

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

            if not isinstance(response, StarletteResponse):
                response = await self.convert_endpoint_result(
                    request, response, mode=None, kind=self.hedron_kind or "page"
                )
            elif policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(response, policy, request=request)
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
        vary = {"Vary": "HX-Request, HX-History-Restore-Request"}

        if isinstance(result, StarletteResponse):
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(result, policy, request=request)
            return result
        if isinstance(result, InteractionResult):
            return await HedronRoute._convert_interaction_result(
                request,
                result,
                mode=mode,
                kind=kind,
                policy=policy,
                authenticated=authenticated,
            )
        if isinstance(result, HTML):
            response = render_component_response(
                result,
                request=request,
                context=render_context_from_request(request),
                policy=policy,
                authenticated=authenticated,
                extra_headers=vary,
            )
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(response, policy, request=request)
            return response
        if isinstance(result, Model) and not isinstance(result, Component):
            from fastapi.encoders import jsonable_encoder
            from fastapi.responses import JSONResponse

            return JSONResponse(jsonable_encoder(result))
        if isinstance(result, Component) or callable(getattr(result, "render", None)):
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
                extra_headers=vary,
            )
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(response, policy, request=request)
            return response
        raise TypeError(f"Unsupported Hedron endpoint return type: {type(result)!r}")

    @staticmethod
    async def _convert_interaction_result(
        request: Request,
        result: InteractionResult,
        *,
        mode: RenderMode | None,
        kind: str,
        policy: SecurityPolicy,
        authenticated: bool,
    ) -> StarletteResponse:
        from starlette.responses import Response

        if result.status_code == 204 or result.content is None and result.status_code == 204:
            headers = interaction_headers(result, request=request)
            return Response(status_code=204, headers=headers)

        target = request.headers.get("HX-Target")
        region = None
        if result.policy is not None and result.policy.declared_regions:
            region = resolve_fragment_region(result.policy, result.region_id or target)

        content: Any = result.content
        if result.oob:
            nodes: list[Any] = []
            if content is not None:
                nodes.append(content)
            for update in result.oob:
                nodes.append(update.content)
            content = Fragment(*nodes)

        headers = interaction_headers(result, request=request)
        if region is not None and result.policy and result.policy.vary_on_target:
            existing = {p.strip() for p in headers.get("Vary", "").split(",") if p.strip()}
            existing.update({"HX-Request", "HX-History-Restore-Request", "HX-Target"})
            headers["Vary"] = ", ".join(sorted(existing))

        force = mode
        if kind == "component":
            force = force or RenderMode.FRAGMENT
        if content is None:
            return Response(status_code=result.status_code, headers=headers)
        response = render_component_response(
            content,
            request=request,
            context=render_context_from_request(request),
            mode=force,
            policy=policy,
            authenticated=authenticated,
            extra_headers=headers,
            status_code=result.status_code,
        )
        if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
            ensure_csrf_cookie(response, policy, request=request)
        return response
