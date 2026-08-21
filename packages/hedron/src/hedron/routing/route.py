"""HedronRoute — APIRoute subclass with component return handling."""

from __future__ import annotations

import asyncio
import contextlib
import functools
import inspect
import logging
import time
from collections.abc import Callable, Coroutine
from typing import Any, Protocol, TypeAlias, runtime_checkable

from fastapi import Request
from fastapi.routing import APIRoute
from starlette.responses import Response as StarletteResponse

from hedron.async_utils import await_if_needed
from hedron.context import render_context_from_request
from hedron.responses import (
    HTML,
    _fragment_region_http_detail,
    render_component_response,
    render_interaction,
)
from hedron.security.csrf import ensure_csrf_cookie
from hedron.security.policy import SecurityPolicy
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import FragmentRegion, FragmentRegionError, InteractionResult
from hedron_core.models import Model
from hedron_core.rendering import RenderMode

_logger = logging.getLogger("hedron.routing.route")

__all__ = ["HedronRoute", "HedronEndpointResult"]


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
    hedron_provenance: str = ""

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
        with contextlib.suppress(TypeError, ValueError):
            wrapped.__signature__ = inspect.signature(endpoint)  # type: ignore[attr-defined]
        return wrapped

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, StarletteResponse]]:
        original = super().get_route_handler()

        async def handler(request: Request) -> StarletteResponse:
            from fastapi import HTTPException, status

            from hedron.routing.router import current_request
            from hedron_core.codes import HED_TYPE_0003
            from hedron_core.htmx_eval import reset_htmx_eval_allowed, set_htmx_eval_allowed

            allowed = getattr(self.endpoint, "_hedron_form_media", None)
            if allowed:
                raw = str(request.headers.get("content-type") or "")
                media = raw.split(";", 1)[0].strip().lower()
                if media not in allowed:
                    raise HTTPException(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        detail=HED_TYPE_0003,
                    )

            policy: SecurityPolicy = getattr(
                request.app.state, "hedron_security", SecurityPolicy.from_name("standard")
            )
            token = current_request.set(request)
            eval_token = set_htmx_eval_allowed(policy.allow_htmx_eval)
            try:
                response = await original(request)
            finally:
                current_request.reset(token)
                reset_htmx_eval_allowed(eval_token)

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
        allow_undeclared_targets: bool = False,
    ) -> StarletteResponse:
        policy: SecurityPolicy = getattr(
            request.app.state, "hedron_security", SecurityPolicy.from_name("standard")
        )
        authenticated = bool(getattr(request.state, "hedron_authenticated", False))
        result = await await_if_needed(result)
        vary = {"Vary": "HX-Request, HX-History-Restore-Request"}

        from hedron_core.diagnostics import HedronError
        from hedron_core.updates import compile_to_interaction

        app_id = getattr(getattr(request.app, "state", None), "hedron_app_id", None)
        try:
            compiled = compile_to_interaction(result, expected_app_id=app_id)
        except HedronError as exc:
            from fastapi import HTTPException

            code = getattr(exc.diagnostic, "code", "")
            status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
            raise HTTPException(status_code=status, detail=str(exc)) from exc
        if isinstance(compiled, InteractionResult):
            result = compiled

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
                allow_undeclared_targets=allow_undeclared_targets,
            )
        if isinstance(result, HTML):
            _authorize_component_fragment(
                request,
                fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                allow_missing_target=kind == "action",
            )
            await _prepare_endpoint_value(result.value, request=request)
            response = render_component_response(
                result,
                request=request,
                context=render_context_from_request(request),
                policy=policy,
                authenticated=authenticated,
                extra_headers=vary,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                allow_missing_target=kind == "action",
            )
            if policy.csrf_enabled and request.method.upper() in {"GET", "HEAD"}:
                ensure_csrf_cookie(response, policy, request=request)
            return response
        if isinstance(result, Model) and not isinstance(result, Component):
            from fastapi.encoders import jsonable_encoder
            from fastapi.responses import JSONResponse

            return JSONResponse(jsonable_encoder(result))
        if isinstance(result, Component) or callable(getattr(result, "render", None)):
            _authorize_component_fragment(
                request,
                fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                allow_missing_target=kind == "action",
            )
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
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                allow_missing_target=kind == "action",
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
        allow_undeclared_targets: bool = False,
    ) -> StarletteResponse:
        """Deprecated private alias — prefer :func:`hedron.responses.render_interaction`."""
        return await render_interaction(
            request,
            result,
            policy=policy,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            mode=mode,
            kind=kind,
            allow_undeclared_targets=allow_undeclared_targets,
        )


def _prepare_deadline_header_trusted(request: Request) -> bool:
    """Return True when ``X-Hedron-Prepare-Deadline`` may shorten prepare deadlines."""
    import os

    peers: set[str] = set()
    raw_env = os.environ.get("HEDRON_TRUSTED_PROXIES", "")
    peers.update(part.strip() for part in raw_env.split(",") if part.strip())
    app = request.scope.get("app") if isinstance(request.scope, dict) else None
    state = getattr(app, "state", None) if app is not None else None
    configured = getattr(state, "hedron_trusted_peers", None) if state is not None else None
    if isinstance(configured, (list, tuple, set, frozenset)):
        peers.update(str(item).strip() for item in configured if str(item).strip())
    if not peers:
        return False
    client = request.scope.get("client") if isinstance(request.scope, dict) else None
    peer = client[0] if isinstance(client, (list, tuple)) and client else None
    return peer is not None and peer in peers


async def _prepare_endpoint_value(value: NodeLike, *, request: Request) -> None:
    """Run optional prepare() hooks before sync render."""
    from hedron.concurrency import _get_limiter, get_concurrency_config
    from hedron.tracing import span
    from hedron_core.prepare import PrepareContext, prepare_tree

    disconnect = asyncio.Event()
    cfg = get_concurrency_config()
    deadline: float | None = None
    if cfg.prepare_deadline_seconds is not None and cfg.prepare_deadline_seconds > 0:
        deadline = time.monotonic() + cfg.prepare_deadline_seconds
    # Client deadlines are ignored unless the peer is an allowlisted proxy
    # (same trust model as mount / CSRF X-Forwarded-Proto).
    header_deadline = request.headers.get("X-Hedron-Prepare-Deadline")
    if header_deadline and _prepare_deadline_header_trusted(request):
        try:
            secs = float(header_deadline)
            if secs > 0:
                header_end = time.monotonic() + secs
                deadline = header_end if deadline is None else min(deadline, header_end)
        except ValueError:
            pass
    ctx = PrepareContext(
        cancel_event=disconnect,
        disconnect_capable=True,
        deadline=deadline,
    )

    async def _watch_disconnect() -> None:
        try:
            while not disconnect.is_set():
                if await request.is_disconnected():
                    disconnect.set()
                    return
                await asyncio.sleep(0.05)
        except Exception:
            _logger.debug("client disconnect watcher ended early", exc_info=True)
            return

    watcher = asyncio.create_task(_watch_disconnect())
    try:
        with span("hedron.prepare", route=str(request.url.path)):
            limiter = _get_limiter()
            await prepare_tree(
                value,
                context=ctx,
                run=limiter.run if cfg.enabled else None,
                concurrency_limit=None if cfg.enabled else cfg.max_in_flight,
            )
    finally:
        disconnect.set()
        watcher.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await watcher


def _authorize_component_fragment(
    request: Request,
    fragment_regions: tuple[FragmentRegion, ...],
    *,
    allow_undeclared_targets: bool = False,
    allow_missing_target: bool = False,
) -> None:
    """Fail closed when HTMX targets an undeclared region for Component returns."""
    from fastapi import HTTPException

    from hedron_core.interaction import InteractionPolicy, authorize_htmx_target

    target = request.headers.get("HX-Target")
    is_htmx = (request.headers.get("HX-Request") or "").lower() == "true"
    if not is_htmx:
        return
    history_restore = (request.headers.get("HX-History-Restore-Request") or "").lower() == "true"
    from hedron_core.updates import matches_declared_host

    handle_hosts = tuple(
        region
        for region in fragment_regions
        if region.id.startswith("h-view-") or region.selector.startswith("#h-view-")
    )
    if handle_hosts:
        if target and any(matches_declared_host(region, target) for region in handle_hosts):
            return
        if target:
            from hedron_core.audit import SecurityAuditEventType, emit_security_audit

            mismatch = FragmentRegionError(
                f"HX-Target {target!r} disagrees with owned handle host",
                requested=target,
                declared=tuple(region.selector for region in handle_hosts),
            )
            emit_security_audit(
                SecurityAuditEventType.HTMX_TARGET_REJECTED,
                str(mismatch),
                attributes={"path": str(request.url.path), "target": target},
            )
            raise HTTPException(
                status_code=403,
                detail=_fragment_region_http_detail(mismatch, request=request),
            )
    # Empty fragment_regions still fail closed when the client sends HX-Target
    # (same contract as InteractionResult / authorize_htmx_target).
    try:
        authorize_htmx_target(
            InteractionPolicy(
                declared_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            ),
            target,
            is_htmx=True,
            history_restore=history_restore,
            allow_missing_target=allow_missing_target,
        )
    except FragmentRegionError as exc:
        from hedron_core.audit import SecurityAuditEventType, emit_security_audit

        emit_security_audit(
            SecurityAuditEventType.HTMX_TARGET_REJECTED,
            str(exc),
            attributes={"path": str(request.url.path), "target": target},
        )
        raise HTTPException(
            status_code=403,
            detail=_fragment_region_http_detail(exc, request=request),
        ) from exc
