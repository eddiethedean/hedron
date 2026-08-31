"""HedronRouter with canonical page, view, and action registration."""

from __future__ import annotations

import functools
import inspect
import secrets
from collections.abc import Awaitable, Callable, Sequence
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, ParamSpec, TypedDict, TypeVar, cast

from fastapi import FastAPI, params
from fastapi.routing import APIRouter
from starlette.datastructures import State
from starlette.requests import Request
from starlette.responses import Response

from hedron.async_utils import await_if_needed
from hedron.fastapi_compat import cached_openapi
from hedron.openapi import operation_id_for
from hedron.replay import ReplayOutcome, ReplayStore
from hedron.routing.route import HedronEndpointResult, HedronRoute
from hedron.security.csrf import prepare_csrf_from_request, validate_csrf
from hedron.security.policy import SecurityPolicy
from hedron_core.addressable import AddressableDescriptor
from hedron_core.alpine import BrowserPlanClosure
from hedron_core.identifiers import component_type_id
from hedron_core.interaction import FragmentRegion
from hedron_core.registry import register_route
from hedron_core.rendering import RenderMode
from hedron_core.request_context import current_request as _portable_current_request

P = ParamSpec("P")
R = TypeVar("R")

IdempotencyMode = Literal["off", "optional", "required"]

__all__ = ["HedronRouter", "current_request"]

current_request = cast(ContextVar[Request[State] | None], _portable_current_request)

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _replay_user_identity(user: object | None) -> str:
    """Read an authentication identity without invoking unsafe properties.

    Starlette's ``SimpleUser`` exposes ``identity`` through ``BaseUser`` as a
    property that raises ``NotImplementedError``.  Authentication middleware is
    allowed to provide any ASGI user object, so identity extraction must be
    best-effort and fall back to the other conventional fields.
    """
    if user is None:
        return "anonymous"
    for name in ("identity", "username", "user_id", "id", "display_name"):
        try:
            value = getattr(user, name, None)
        except (AttributeError, NotImplementedError, TypeError, ValueError):
            value = None
        text = str(value).strip() if value is not None else ""
        if text and text.lower() != "anonymous":
            return text
    return "anonymous"


def _anonymous_replay_binding(request: Request[State]) -> str:
    """Return a stable per-client binding for anonymous replay scopes.

    Cookie-backed CSRF tokens are already unique to an anonymous browser and
    are available on normal unsafe actions.  Non-cookie strategies can use the
    submitted token only after the unsafe-action CSRF check has validated it.
    If no authoritative client material exists (for example, CSRF is disabled),
    use a request-local nonce rather than the process-wide ``anon:none``
    sentinel, which would let unrelated callers share cached responses.
    """
    app = request.scope.get("app")
    app_state = getattr(app, "state", None) if app is not None else None
    policy = getattr(app_state, "hedron_security", None)
    cookie_name = getattr(policy, "csrf_cookie_name", "hedron_csrf")
    strategy = policy.resolve_csrf_strategy() if policy is not None else None
    candidate = getattr(strategy, "cookie_name", None)
    if isinstance(candidate, str) and candidate:
        cookie_name = candidate
    cookies = getattr(request, "cookies", {}) or {}
    binding = cookies.get(cookie_name) if isinstance(cookie_name, str) else None
    if isinstance(binding, str) and binding:
        return binding
    if strategy is not None and request.method.upper() not in _SAFE_METHODS:
        header_name = getattr(strategy, "header_name", "")
        header_binding = request.headers.get(header_name) if isinstance(header_name, str) else None
        form_binding = getattr(request.state, "hedron_csrf_form_token", None)
        binding = form_binding or header_binding
        if isinstance(binding, str) and binding:
            # _wrap_endpoint runs CSRF validation before replay claiming, so this
            # is authoritative for unsafe requests with an active strategy.
            return binding
    state_nonce = getattr(request.state, "hedron_replay_anonymous_nonce", None)
    if not isinstance(state_nonce, str) or not state_nonce:
        state_nonce = secrets.token_urlsafe(32)
        request.state.hedron_replay_anonymous_nonce = state_nonce
    return state_nonce


class _FragmentRegionMeta(TypedDict):
    id: str
    selector: str
    description: str


@dataclass(slots=True)
class _ReplayGuard:
    """In-flight idempotency claim held across endpoint execution."""

    claim: ReplayOutcome
    store: ReplayStore
    key: str
    fingerprint: str
    scope_key: str


def _logical_id(fn: Callable[..., object], distribution: str = "hedron") -> str:
    module = getattr(fn, "__module__", None) or "hedron"
    name = getattr(fn, "__name__", None) or "endpoint"
    return component_type_id(distribution, module, name)


def _requires_csrf(methods: Sequence[str]) -> bool:
    return any(m.upper() not in _SAFE_METHODS for m in methods)


def _fragment_regions_for_inference(
    regions: Sequence[FragmentRegion],
) -> list[_FragmentRegionMeta]:
    """Typed nested metadata for route documents (ROUTE-053; never stringify)."""
    return [
        {
            "id": region.id,
            "selector": region.selector,
            "description": region.description,
        }
        for region in regions
    ]


def normalize_fragment_regions(
    fragment_regions: Sequence[FragmentRegion | str] | FragmentRegion | str | None,
) -> tuple[FragmentRegion, ...]:
    if not fragment_regions:
        return ()
    if isinstance(fragment_regions, (FragmentRegion, str)):
        fragment_regions = (fragment_regions,)
    out: list[FragmentRegion] = []
    for r in fragment_regions:
        if isinstance(r, FragmentRegion):
            out.append(r)
            continue
        name = str(r).removeprefix("#")
        out.append(FragmentRegion(id=name, selector=f"#{name}"))
    return tuple(out)


# Compatibility alias retained for integrations that imported the former private name.
_normalize_fragment_regions = normalize_fragment_regions


def _set_hedron_attr(target: object, name: str, value: object) -> None:
    """Attach dynamic Hedron metadata without attr-defined ignores."""
    setattr(target, name, value)


def _annotate_callable(
    target: Callable[..., object],
    *,
    fragment_regions: tuple[FragmentRegion, ...] | None = None,
    capability: str | None = None,
    idempotency: str | None = None,
    view_logical_id: object | None = None,
) -> None:
    if fragment_regions is not None:
        _set_hedron_attr(target, "_hedron_fragment_regions", fragment_regions)
    if capability:
        _set_hedron_attr(target, "_hedron_capability", capability)
    if idempotency:
        _set_hedron_attr(target, "_hedron_idempotency", idempotency)
    if view_logical_id:
        _set_hedron_attr(target, "_hedron_view_logical_id", view_logical_id)


def _resolve_request(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Request[State] | None:
    request = current_request.get()
    if request is not None:
        return request
    for arg in args:
        if isinstance(arg, Request):
            return cast(Request[State], arg)
    maybe = kwargs.get("request")
    if isinstance(maybe, Request):
        return cast(Request[State], maybe)
    return None


async def _enforce_csrf(request: Request[State], *, require_csrf: bool) -> None:
    if not require_csrf or request.method.upper() in _SAFE_METHODS:
        return
    policy: SecurityPolicy = getattr(
        request.app.state, "hedron_security", SecurityPolicy.from_name("standard")
    )
    await prepare_csrf_from_request(request, policy)
    validate_csrf(request, policy)


async def _begin_replay(
    request: Request[State],
    fn: Callable[..., object],
    *,
    idempotency: str,
) -> _ReplayGuard | Response | None:
    """Claim an idempotency key; return cached Response, guard, or None."""
    from starlette.responses import Response as StarletteResponse

    from hedron.replay import (
        IdempotencyPolicy,
        ReplayState,
        digest_bytes,
        extract_idempotency_key,
        fingerprint_request,
        replay_scope,
        resolve_replay_store,
    )

    # Public action API accepts str; IdempotencyPolicy narrows at this boundary.
    replay_policy = IdempotencyPolicy(mode=cast(IdempotencyMode, idempotency))
    replay_key = await extract_idempotency_key(request, replay_policy)
    if replay_policy.mode == "required" and not replay_key:
        from hedron_core.diagnostics import error

        raise error(
            "HED-REPLAY-0001",
            title="Idempotency key required",
            explanation="This action requires an Idempotency-Key.",
            remediation="Send the Idempotency-Key header or form field.",
        )
    if not replay_key:
        return None

    # Prefer scope["user"] so idempotency works without AuthenticationMiddleware.
    # Accessing request.user asserts that middleware is installed.
    user = request.scope.get("user")
    subject = _replay_user_identity(user)
    tenant = str(getattr(request.state, "hedron_tenant", "") or "")
    session = str(
        getattr(request.state, "session_id", None)
        or request.cookies.get("session")
        or request.cookies.get("hedron_session")
        or ""
    )
    if subject == "anonymous" and not session:
        session = _anonymous_replay_binding(request)
    body_digest = ""
    try:
        raw_body = await request.body()
        body_digest = digest_bytes(raw_body or b"")
    except (RuntimeError, OSError, ValueError, TypeError):
        body_digest = f"len:{request.headers.get('content-length', '')}"
    replay_fp = fingerprint_request(
        action_id=getattr(fn, "__name__", "action"),
        subject=subject,
        tenant=tenant,
        inputs={
            "path": str(request.url.path),
            "method": request.method,
            "query": str(request.url.query),
            "content_type": str(request.headers.get("content-type") or ""),
            "body_sha256": body_digest,
        },
        policy_version=replay_policy.policy_version,
    )
    replay_store = resolve_replay_store(request)
    replay_scope_key = replay_scope(
        tenant=tenant,
        subject=subject,
        action_id=getattr(fn, "__name__", "action"),
        session=session,
    )
    replay_claim = replay_store.claim(
        key=replay_key,
        fingerprint=replay_fp,
        scope=replay_scope_key,
        retention_seconds=replay_policy.retention_seconds,
    )
    if replay_claim.state == ReplayState.CONFLICT:
        from hedron_core.diagnostics import error

        raise error(
            "HED-REPLAY-0002",
            title="Idempotency key conflict",
            explanation="The key was reused with a different request fingerprint.",
            remediation="Use a new key for distinct mutations.",
        )
    if replay_claim.state == ReplayState.IN_FLIGHT:
        from hedron_core.diagnostics import error

        raise error(
            "HED-REPLAY-0003",
            title="Idempotency key in flight",
            explanation="A concurrent request already claimed this key.",
            remediation="Retry after the first request completes.",
        )
    if replay_claim.state == ReplayState.REPLAYED:
        cached_headers = replay_claim.cached_headers
        if cached_headers is None:
            return StarletteResponse(
                content=replay_claim.cached_body or b"",
                status_code=int(replay_claim.cached_status or 200),
                media_type=replay_claim.cached_media_type or "text/html",
                headers={"Hedron-Replay": "true"},
            )
        response = StarletteResponse(
            content=replay_claim.cached_body or b"",
            status_code=int(replay_claim.cached_status or 200),
        )
        response.raw_headers = [
            (name.encode("latin-1"), value.encode("latin-1"))
            for name, value in cached_headers
            if name.lower() != "hedron-replay"
        ]
        response.headers["Hedron-Replay"] = "true"
        return response
    return _ReplayGuard(
        claim=replay_claim,
        store=replay_store,
        key=replay_key,
        fingerprint=replay_fp,
        scope_key=replay_scope_key,
    )


def _abort_replay(guard: _ReplayGuard | None) -> None:
    if guard is None:
        return
    from hedron.replay import ReplayState

    if guard.claim.state == ReplayState.FIRST:
        guard.store.abort(key=guard.key, scope=guard.scope_key, fingerprint=guard.fingerprint)


def _replay_store_accepts_headers(store: ReplayStore) -> bool:
    """Return whether a replay store supports the optional response-header field.

    ``ReplayStore`` is a public extension point. Stores written before response
    headers were added have a narrower ``complete`` signature and must keep
    working while applications migrate them.
    """
    try:
        parameters = inspect.signature(store.complete).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(
        parameter.name == "headers" or parameter.kind is inspect.Parameter.VAR_KEYWORD
        for parameter in parameters
    )


def _complete_replay(guard: _ReplayGuard | None, response: Response) -> None:
    if guard is None:
        return
    from starlette.responses import StreamingResponse

    from hedron.replay import ReplayState

    if guard.claim.state != ReplayState.FIRST:
        return
    # Streaming bodies are not materialized; refuse to cache an empty replay.
    if isinstance(response, StreamingResponse):
        _abort_replay(guard)
        return
    body = getattr(response, "body", None)
    if body is None and hasattr(response, "render"):
        # Materialize Starlette Response body when not yet sent.
        try:
            body = response.render(getattr(response, "content", b""))
        except (AttributeError, TypeError, ValueError, RuntimeError):
            body = b""
    if body is None:
        body = b""
    if isinstance(body, memoryview):
        body = body.tobytes()
    if isinstance(body, str):
        body = body.encode("utf-8")
    media_type = getattr(response, "media_type", None) or "text/html"
    raw_headers = getattr(response, "raw_headers", ())
    headers = tuple(
        (name.decode("latin-1"), value.decode("latin-1"))
        for name, value in raw_headers
        if isinstance(name, bytes) and isinstance(value, bytes)
    )
    status = int(getattr(response, "status_code", 200) or 200)
    if _replay_store_accepts_headers(guard.store):
        guard.store.complete(
            key=guard.key,
            scope=guard.scope_key,
            fingerprint=guard.fingerprint,
            status=status,
            body=bytes(body),
            media_type=str(media_type),
            headers=headers,
        )
    else:
        guard.store.complete(
            key=guard.key,
            scope=guard.scope_key,
            fingerprint=guard.fingerprint,
            status=status,
            body=bytes(body),
            media_type=str(media_type),
        )


def _apply_fastapi_signature(
    endpoint: Callable[..., Any],
    fn: Callable[..., object],
) -> None:
    """Preserve FastAPI-visible annotations/signature after wrapping."""
    import typing

    # Resolve annotations in the original function's globals so Depends survives wrapping.
    try:
        hints = typing.get_type_hints(fn, include_extras=True)
    except (NameError, TypeError, AttributeError, RecursionError):
        # Nested locals / unresolved forward refs — FastAPI still gets a usable signature.
        hints = {}
    sig = inspect.signature(fn)
    params = [
        # Type-authoring may have installed a concrete FastAPI signature on the
        # function before it reaches the router.  Preserve those annotations;
        # replacing them with the original type hints silently turns native
        # query models back into request bodies.
        param.replace(annotation=hints[name])
        if isinstance(param.annotation, str) and name in hints
        else param
        for name, param in sig.parameters.items()
    ]
    # FastAPI reads __signature__ from wrapped callables; not on Callable typing.
    endpoint.__signature__ = sig.replace(  # type: ignore[attr-defined]
        parameters=params,
        return_annotation=(
            hints.get("return", sig.return_annotation)
            if isinstance(sig.return_annotation, str)
            else sig.return_annotation
        ),
    )


def _wrap_endpoint(
    fn: Callable[..., object],
    *,
    kind: str,
    mode: RenderMode | None,
    require_csrf: bool,
    fragment_regions: tuple[FragmentRegion, ...] = (),
    allow_undeclared_targets: bool = False,
    capability: str | None = None,
    idempotency: str | None = None,
    browser_closure: BrowserPlanClosure | None = None,
) -> Callable[..., Response | Awaitable[Response]]:
    @functools.wraps(fn)
    async def endpoint(*args: Any, **kwargs: Any) -> Response:
        request = _resolve_request(args, kwargs)
        if request is None:
            raise RuntimeError("Hedron endpoints require an active Request")
        await _enforce_csrf(request, require_csrf=require_csrf)
        # CAP-055: enforce capability after CSRF, before side effects.
        if capability:
            from hedron.capabilities import enforce_capability

            enforce_capability(request, capability)
        replay_guard: _ReplayGuard | None = None
        if idempotency and idempotency != "off":
            begun = await _begin_replay(request, fn, idempotency=idempotency)
            if isinstance(begun, Response):
                return begun
            replay_guard = begun
        try:
            result = fn(*args, **kwargs)
            result = await await_if_needed(result)
            # Endpoint returns are untyped callables; narrow at the convert boundary.
            response = await HedronRoute.convert_endpoint_result(
                request,
                cast(HedronEndpointResult, result),
                mode=mode,
                kind=kind,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
                browser_closure=browser_closure,
            )
        except BaseException:
            # CancelledError is BaseException — abort so claims do not stick IN_FLIGHT.
            _abort_replay(replay_guard)
            raise
        _complete_replay(replay_guard, response)
        return response

    _apply_fastapi_signature(endpoint, fn)
    _annotate_callable(
        endpoint,
        fragment_regions=fragment_regions,
        capability=capability,
        idempotency=idempotency,
        view_logical_id=getattr(fn, "_hedron_view_logical_id", None),
    )
    return endpoint


class HedronRouter(APIRouter):
    """APIRouter with Hedron page/component/action decorators."""

    def __init__(self, *args: Any, provenance: str = "", **kwargs: Any) -> None:
        kwargs.setdefault("route_class", HedronRoute)
        super().__init__(*args, **kwargs)
        self.hedron_provenance = provenance or str(self.prefix or "")
        self._hedron_host_app: object | None = None

    def _fail_closed_late(self) -> None:
        with self._runtime_scope():
            self._fail_closed_late_scoped()

    @contextmanager
    def _runtime_scope(self):
        host = self._hedron_host_app
        runtime = getattr(host, "_hedron_runtime", None)
        if runtime is None:
            yield
            return
        with runtime.activate():
            yield

    def _fail_closed_late_scoped(self) -> None:
        from hedron.registration import fail_closed_late_registration
        from hedron_core.catalog import get_sealed_catalog
        from hedron_core.registry.builder import active_builder

        host = self._hedron_host_app
        fail_closed_late_registration(
            registry_sealed=active_builder().is_sealed,
            catalog_sealed=get_sealed_catalog() is not None,
            openapi_cached=cached_openapi(cast(FastAPI | None, host)) is not None,
        )

    def attach_host_app(self, app: object) -> None:
        """Associate this router with the application that owns registration state."""
        self._hedron_host_app = app
        runtime = getattr(app, "_hedron_runtime", None)
        if runtime is not None:
            from hedron_core.registry.builder import bind_compatibility_builder

            bind_compatibility_builder(runtime.registry)

    def add_api_route(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]  # FastAPI parent kwargs are version-sensitive; keep *args/**kwargs.
        self._fail_closed_late()
        super().add_api_route(*args, **kwargs)
        if self.routes:
            # BaseRoute has no hedron_provenance; setattr preserves non-HedronRoute route_class.
            _set_hedron_attr(
                self.routes[-1],
                "hedron_provenance",
                self.hedron_provenance or self.prefix,
            )

    def include_router(self, router: Any, *args: Any, **kwargs: Any) -> None:  # type: ignore[override]  # FastAPI parent kwargs are version-sensitive; keep *args/**kwargs.
        self._fail_closed_late()
        if isinstance(router, HedronRouter) and self._hedron_host_app is not None:
            router.attach_host_app(self._hedron_host_app)
        super().include_router(router, *args, **kwargs)

    def _register_route_or_rollback(self, **kwargs: Any) -> None:
        try:
            with self._runtime_scope():
                register_route(**kwargs)
        except Exception:
            if self.routes:
                self.routes.pop()
            raise

    def page(
        self,
        path: str,
        *,
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        browser_closure: BrowserPlanClosure | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            from hedron.responses import PageResponse

            route_name = name or fn.__name__
            logical_id = _logical_id(fn)
            verb_list = list(methods or ["GET"])
            op_id = operation_id_for("page", route_name, path, verb_list[0])
            regions = normalize_fragment_regions(fragment_regions)
            _annotate_callable(fn, fragment_regions=regions)
            wrapped = _wrap_endpoint(
                fn,
                kind="page",
                mode=None,
                require_csrf=_requires_csrf(verb_list),
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
                browser_closure=browser_closure,
            )
            self.add_api_route(
                path,
                wrapped,
                methods=verb_list,
                name=route_name,
                operation_id=op_id,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                tags=tags,
                response_class=kwargs.pop("response_class", None) or PageResponse,
                response_model=None,
                **kwargs,
            )
            self._register_route_or_rollback(
                kind="page",
                logical_id=logical_id,
                name=route_name,
                path=f"{self.prefix}{path}",
                methods=tuple(m.upper() for m in verb_list),
                operation_id=op_id,
                include_in_schema=include_in_schema,
                module=fn.__module__,
                tags=tuple(str(t) for t in (tags or ())),
                docs=inspect.getdoc(fn),
                endpoint=fn,
                htmx_inference={
                    "page_fragment": "HX-Request selects FRAGMENT vs PAGE",
                    "history": "browser history for full-page navigation",
                    "fragment_regions": _fragment_regions_for_inference(regions),
                    "boosted": "title/history/assets preserved; full-page fallback required",
                },
            )
            return fn

        return decorator

    def _view_route(
        self,
        path: str,
        *,
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        _route_kind: str = "component",
        browser_closure: BrowserPlanClosure | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            from hedron.responses import FragmentResponse

            route_name = name or fn.__name__
            logical_id = _logical_id(fn)
            verb_list = list(methods or ["GET"])
            if _route_kind not in {"component", "view"}:
                raise ValueError("_route_kind must be component or view")
            op_id = operation_id_for(_route_kind, route_name, path, verb_list[0])
            regions = normalize_fragment_regions(fragment_regions)
            _annotate_callable(fn, fragment_regions=regions)
            wrapped = _wrap_endpoint(
                fn,
                kind=_route_kind,
                mode=RenderMode.FRAGMENT,
                require_csrf=_requires_csrf(verb_list),
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
                browser_closure=browser_closure,
            )
            self.add_api_route(
                path,
                wrapped,
                methods=verb_list,
                name=route_name,
                operation_id=op_id,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                tags=tags,
                response_class=kwargs.pop("response_class", None) or FragmentResponse,
                response_model=None,
                **kwargs,
            )
            self._register_route_or_rollback(
                kind=_route_kind,
                logical_id=logical_id,
                name=route_name,
                path=f"{self.prefix}{path}",
                methods=tuple(m.upper() for m in verb_list),
                operation_id=op_id,
                include_in_schema=include_in_schema,
                module=fn.__module__,
                tags=tuple(str(t) for t in (tags or ())),
                docs=inspect.getdoc(fn),
                endpoint=fn,
                htmx_inference={
                    "default_mode": "fragment",
                    "target": "caller-provided hx-target",
                    "swap": "outerHTML",
                    "fragment_regions": _fragment_regions_for_inference(regions),
                    "csrf_required": str(_requires_csrf(verb_list)).lower(),
                },
            )
            return fn

        return decorator

    def view(
        self,
        path: str,
        *,
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = False,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        browser_closure: BrowserPlanClosure | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """Canonical view spelling over the existing safe fragment transport."""
        return self._view_route(
            path,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
            dependencies=dependencies,
            tags=tags,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
            _route_kind="view",
            browser_closure=browser_closure,
            **kwargs,
        )

    def action(
        self,
        path: str,
        *,
        method: str = "POST",
        methods: Sequence[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        dependencies: Sequence[params.Depends] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        capability: str | None = None,
        idempotency: str | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        verb_list = list(methods or [method])

        def decorator(fn: Callable[P, R]) -> Callable[P, R]:
            from hedron.responses import FragmentResponse

            route_name = name or fn.__name__
            logical_id = _logical_id(fn)
            primary = verb_list[0].upper()
            op_id = operation_id_for("action", route_name, path, primary)
            regions = normalize_fragment_regions(fragment_regions)
            _annotate_callable(
                fn,
                fragment_regions=regions,
                capability=capability,
                idempotency=idempotency,
            )
            wrapped = _wrap_endpoint(
                fn,
                kind="action",
                mode=RenderMode.FRAGMENT,
                require_csrf=_requires_csrf(verb_list),
                fragment_regions=regions,
                allow_undeclared_targets=allow_undeclared_targets,
                capability=capability,
                idempotency=idempotency,
            )
            self.add_api_route(
                path,
                wrapped,
                methods=verb_list,
                name=route_name,
                operation_id=op_id,
                include_in_schema=include_in_schema,
                dependencies=dependencies,
                tags=tags,
                response_class=kwargs.pop("response_class", None) or FragmentResponse,
                response_model=None,
                **kwargs,
            )
            route = self.routes[-1]
            if isinstance(route, HedronRoute):
                route.hedron_kind = "action"
            safety = "legacy"
            if idempotency and idempotency != "off":
                safety = f"idempotent:{idempotency}"
            self._register_route_or_rollback(
                kind="action",
                logical_id=logical_id,
                name=route_name,
                path=f"{self.prefix}{path}",
                methods=tuple(m.upper() for m in verb_list),
                operation_id=op_id,
                include_in_schema=include_in_schema,
                module=fn.__module__,
                tags=tuple(str(t) for t in (tags or ())),
                docs=inspect.getdoc(fn),
                endpoint=fn,
                htmx_inference={
                    "csrf": "required for unsafe cookie-authenticated methods",
                    "swap": "innerHTML",
                    "validation_fragment": "form error components",
                    "fragment_regions": _fragment_regions_for_inference(regions),
                    "capability": capability or "",
                    "action_safety": safety,
                },
            )
            return fn

        return decorator

    def include_component(
        self,
        descriptor: AddressableDescriptor[P, R] | Callable[P, R],
        *,
        path: str,
        name: str | None = None,
        dependencies: Sequence[params.Depends] | None = None,
        include_in_schema: bool | None = None,
        methods: Sequence[str] | None = None,
        tags: list[str | Enum] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **kwargs: Any,
    ) -> None:
        from hedron.responses import FragmentResponse

        if isinstance(descriptor, AddressableDescriptor):
            factory = descriptor.factory
            route_name = name or descriptor.name
            logical_id = descriptor.logical_id
            verb_list = list(methods or descriptor.methods)
            schema = (
                descriptor.include_in_schema if include_in_schema is None else include_in_schema
            )
            tag_list: list[str | Enum] = list(tags) if tags is not None else list(descriptor.tags)
        else:
            factory = descriptor
            route_name = name or factory.__name__
            logical_id = _logical_id(factory)
            verb_list = list(methods or ["GET"])
            schema = False if include_in_schema is None else include_in_schema
            tag_list = list(tags or [])

        regions = normalize_fragment_regions(fragment_regions)
        _annotate_callable(factory, fragment_regions=regions)
        op_id = operation_id_for("component", route_name, path, verb_list[0])
        wrapped = _wrap_endpoint(
            factory,
            kind="component",
            mode=RenderMode.FRAGMENT,
            require_csrf=_requires_csrf(verb_list),
            fragment_regions=regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
        self.add_api_route(
            path,
            wrapped,
            methods=verb_list,
            name=route_name,
            operation_id=op_id,
            include_in_schema=schema,
            dependencies=dependencies,
            tags=tag_list or None,
            response_class=kwargs.pop("response_class", None) or FragmentResponse,
            response_model=None,
            **kwargs,
        )
        self._register_route_or_rollback(
            kind="component",
            logical_id=logical_id,
            name=route_name,
            path=f"{self.prefix}{path}",
            methods=tuple(m.upper() for m in verb_list),
            operation_id=op_id,
            include_in_schema=schema,
            module=factory.__module__,
            tags=tuple(str(t) for t in tag_list),
            docs=inspect.getdoc(factory),
            endpoint=factory,
            htmx_inference={
                "default_mode": "fragment",
                "exposure": "include_component",
                "fragment_regions": _fragment_regions_for_inference(regions),
            },
        )
