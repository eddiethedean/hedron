"""HedronRoute — APIRoute subclass with component return handling."""

from __future__ import annotations

import asyncio
import functools
import inspect
from collections.abc import Callable, Coroutine
from typing import Any, Protocol, TypeAlias, runtime_checkable

from fastapi import Request
from fastapi.routing import APIRoute
from starlette.responses import Response as StarletteResponse

from hedron.async_utils import await_if_needed
from hedron.context import render_context_from_request
from hedron.interaction import (
    FragmentRegion,
    FragmentRegionError,
    InteractionResult,
    interaction_headers,
)
from hedron.responses import HTML, render_component_response
from hedron.security.csrf import ensure_csrf_cookie
from hedron.security.policy import SecurityPolicy
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import materialize_interaction_nodes
from hedron_core.models import Model
from hedron_core.rendering import RenderMode

__all__ = ["HedronRoute"]


@runtime_checkable
class _SupportsRender(Protocol):
    def render(self, *args: Any, **kwargs: Any) -> object: ...


HedronEndpointResult: TypeAlias = (
    StarletteResponse | InteractionResult | HTML | Component[Any] | Model | _SupportsRender
)


def _is_hedron_value(value: object) -> bool:
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
        result: HedronEndpointResult,
        *,
        mode: RenderMode | None = None,
        kind: str = "page",
        fragment_regions: tuple[FragmentRegion, ...] = (),
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
                fragment_regions=fragment_regions,
            )
        if isinstance(result, HTML):
            await _prepare_endpoint_value(result.value, request=request)
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
            await _prepare_endpoint_value(result, request=request)  # type: ignore[arg-type]
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
        fragment_regions: tuple[FragmentRegion, ...] = (),
    ) -> StarletteResponse:
        from fastapi import HTTPException
        from starlette.responses import Response

        from hedron.interaction import merge_route_regions

        if fragment_regions:
            result = merge_route_regions(result, fragment_regions)

        if result.status_code == 204 or result.content is None and result.status_code == 204:
            headers = interaction_headers(result, request=request)
            return Response(status_code=204, headers=headers)

        target = request.headers.get("HX-Target")
        is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
        try:
            from hedron_core.interaction import authorize_htmx_target

            region = authorize_htmx_target(
                result.policy,
                result.region_id or target,
                is_htmx=is_htmx,
            )
        except FragmentRegionError as exc:
            from hedron_core.audit import SecurityAuditEventType, emit_security_audit

            emit_security_audit(
                SecurityAuditEventType.HTMX_TARGET_REJECTED,
                str(exc),
                attributes={"path": str(request.url.path), "target": target},
            )
            raise HTTPException(status_code=403, detail=str(exc)) from exc

        content: NodeLike | None = result.content
        if result.oob:
            try:
                content = materialize_interaction_nodes(result)
            except (FragmentRegionError, ValueError) as exc:
                raise HTTPException(status_code=403, detail=str(exc)) from exc

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
        await _prepare_endpoint_value(content, request=request)
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


async def _prepare_endpoint_value(value: NodeLike, *, request: Request) -> None:
    """Run optional prepare() hooks before sync render."""
    from hedron.concurrency import get_concurrency_config
    from hedron.tracing import span
    from hedron_core.prepare import PrepareContext, prepare_tree

    disconnect = asyncio.Event()
    cfg = get_concurrency_config()
    ctx = PrepareContext(
        cancel_event=disconnect,
        disconnect_capable=True,
        deadline=None,
    )
    with span("hedron.prepare", route=str(request.url.path)):
        await prepare_tree(
            value,
            context=ctx,
            concurrency_limit=cfg.max_in_flight if cfg.enabled else None,
        )
