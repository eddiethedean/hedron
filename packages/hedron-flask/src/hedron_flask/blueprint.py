"""Flask Blueprint with Hedron page/component/action registration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, Protocol, TypeVar, cast

from flask import Blueprint, Flask, Response, current_app, request

from hedron_core.addressable import AddressableDescriptor
from hedron_core.component import Component, NodeLike
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.rendering import RenderResult
from hedron_core.security_policy import SecurityPolicy, SecurityProfile
from hedron_flask.csrf import DEFAULT_CSRF_COOKIE, assert_flask_csrf_strategy, validate_csrf
from hedron_flask.responses import component_response, interaction_response

__all__ = ["HedronBlueprint", "convert_view_result", "wrap_hedron_view"]

F = TypeVar("F", bound=Callable[..., Any])

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class _AuthSignalLike(Protocol):
    authenticated: bool


class _HedronFlaskExtension(Protocol):
    """Minimal extension surface used by blueprint helpers."""

    csrf_protect: bool
    csrf_cookie_name: str
    csrf_cookie_path: str | None
    csrf_cookie_secure: bool | None
    security_policy: SecurityPolicy | None

    def auth_signal(self, req: object = ...) -> _AuthSignalLike: ...


def _normalize_fragment_regions(
    fragment_regions: Sequence[FragmentRegion | str] | None,
) -> tuple[FragmentRegion, ...]:
    if not fragment_regions:
        return ()
    out: list[FragmentRegion] = []
    for region in fragment_regions:
        if isinstance(region, FragmentRegion):
            out.append(region)
        else:
            name = str(region).removeprefix("#")
            out.append(FragmentRegion(id=name, selector=f"#{name}"))
    return tuple(out)


def convert_view_result(
    value: object,
    *,
    authenticated: bool = False,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> Response | object:
    """Convert Hedron return types to Flask responses; pass through native Responses."""
    if isinstance(value, Response):
        return value
    from hedron_core.diagnostics import HedronError
    from hedron_core.updates import compile_to_interaction

    try:
        value = compile_to_interaction(value)
    except HedronError as exc:
        code = getattr(exc.diagnostic, "code", "")
        status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
        return Response(str(exc), status=status, content_type="text/plain")
    if isinstance(value, InteractionResult):
        return interaction_response(
            value,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    if isinstance(value, RenderResult):
        return component_response(
            value,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
        # Duck-typed component / NodeLike after isinstance/hasattr gate.
        return component_response(
            cast(NodeLike | Component[Any] | RenderResult, value),
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    return value


def _extension() -> _HedronFlaskExtension | None:
    extension = current_app.extensions.get("hedron")
    if extension is None:
        return None
    return cast(_HedronFlaskExtension, extension)


def _authenticated() -> bool:
    auth_fn = getattr(current_app, "auth_signal", None)
    if callable(auth_fn):
        signal = auth_fn(request)
        return bool(getattr(signal, "authenticated", False))
    extension = _extension()
    if extension is not None:
        signal = extension.auth_signal(request)
        return bool(getattr(signal, "authenticated", False))
    return False


def _csrf_settings() -> tuple[bool, str, SecurityPolicy | None]:
    extension = _extension()
    if extension is None:
        return True, DEFAULT_CSRF_COOKIE, None
    protect = bool(getattr(extension, "csrf_protect", True))
    cookie_name = str(getattr(extension, "csrf_cookie_name", DEFAULT_CSRF_COOKIE))
    policy = getattr(extension, "security_policy", None)
    if isinstance(policy, SecurityPolicy) and not policy.csrf_enabled:
        protect = False
    return protect, cookie_name, policy if isinstance(policy, SecurityPolicy) else None


def wrap_hedron_view(
    view: F,
    *,
    require_csrf: bool,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
) -> F:
    regions = _normalize_fragment_regions(fragment_regions)

    @wraps(view)
    def wrapped(*args: object, **kwargs: object) -> object:
        protect, cookie_name, policy = _csrf_settings()
        if require_csrf and protect and request.method.upper() not in _SAFE_METHODS:
            if isinstance(policy, SecurityPolicy):
                validate_csrf(request, cookie_name=cookie_name, policy=policy)
            else:
                validate_csrf(request, cookie_name=cookie_name)
        value = current_app.ensure_sync(view)(*args, **kwargs)
        return convert_view_result(
            value,
            authenticated=_authenticated(),
            fragment_regions=regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )

    return cast(F, wrapped)


# Backward-compatible alias for older internal imports.
_wrap_hedron_view = wrap_hedron_view


class HedronBlueprint(Blueprint):
    """Flask Blueprint with Hedron ``page`` / ``component`` / ``action`` helpers."""

    def page(
        self,
        rule: str,
        *,
        endpoint: str | None = None,
        methods: Sequence[str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **options: Any,
    ) -> Callable[[F], F]:
        method_list = list(methods or ("GET",))
        require_csrf = any(m.upper() not in _SAFE_METHODS for m in method_list)

        def decorator(view: F) -> F:
            wrapped = wrap_hedron_view(
                view,
                require_csrf=require_csrf,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.add_url_rule(
                rule,
                endpoint=endpoint,
                view_func=wrapped,
                methods=method_list,
                **options,
            )
            return view

        return decorator

    def component(
        self,
        rule: str,
        *,
        endpoint: str | None = None,
        methods: Sequence[str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **options: Any,
    ) -> Callable[[F], F]:
        method_list = list(methods or ("GET",))
        require_csrf = any(m.upper() not in _SAFE_METHODS for m in method_list)

        def decorator(view: F) -> F:
            wrapped = wrap_hedron_view(
                view,
                require_csrf=require_csrf,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.add_url_rule(
                rule,
                endpoint=endpoint,
                view_func=wrapped,
                methods=method_list,
                **options,
            )
            return view

        return decorator

    def action(
        self,
        rule: str,
        *,
        endpoint: str | None = None,
        methods: Sequence[str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **options: Any,
    ) -> Callable[[F], F]:
        method_list = list(methods or ("POST",))

        def decorator(view: F) -> F:
            wrapped = wrap_hedron_view(
                view,
                require_csrf=True,
                fragment_regions=fragment_regions,
                allow_undeclared_targets=allow_undeclared_targets,
            )
            self.add_url_rule(
                rule,
                endpoint=endpoint,
                view_func=wrapped,
                methods=method_list,
                **options,
            )
            return view

        return decorator

    def include_component(
        self,
        descriptor: AddressableDescriptor[..., Any],
        *,
        path: str,
        endpoint: str | None = None,
        methods: Sequence[str] | None = None,
        fragment_regions: Sequence[FragmentRegion | str] | None = None,
        allow_undeclared_targets: bool = False,
        **options: Any,
    ) -> None:
        """Expose an ``@addressable`` factory at ``path`` (GET by default)."""

        method_list = list(methods or ("GET",))
        require_csrf = any(m.upper() not in _SAFE_METHODS for m in method_list)
        ep = endpoint or f"hedron_{descriptor.logical_id.replace(':', '_').replace('.', '_')}"

        def view(**kwargs: Any) -> Any:
            return descriptor.factory(**kwargs)

        wrapped = wrap_hedron_view(
            view,
            require_csrf=require_csrf,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
        self.add_url_rule(path, endpoint=ep, view_func=wrapped, methods=method_list, **options)


def _apply_flask_session_cookie_defaults(app: Flask, policy: SecurityPolicy) -> None:
    """Set Secure/SameSite session cookies in production and STRICT profiles (#231)."""
    from hedron_core.compile_gate import is_production_env
    from hedron_flask.csrf import csrf_cookie_force_secure

    force = csrf_cookie_force_secure(None, policy)
    prod = is_production_env() or policy.profile is SecurityProfile.STRICT
    if force is True or prod:
        app.config["SESSION_COOKIE_SECURE"] = True
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def attach_hedron_to_flask(
    app: Flask,
    extension: object,
    *,
    auto_csrf_cookie: bool = True,
    security: object | None = None,
) -> None:
    """Store extension state and apply security headers (and optional CSRF cookies)."""

    import contextlib
    from dataclasses import replace

    from hedron_core.adapter import AuthSignal

    ext = cast(_HedronFlaskExtension, extension)
    policy = (
        SecurityPolicy.from_name(cast(str | SecurityPolicy, security))
        if security is not None
        else getattr(ext, "security_policy", None)
    )
    if policy is None:
        policy = SecurityPolicy.from_name("standard")
    if not isinstance(policy, SecurityPolicy):
        policy = SecurityPolicy.from_name(cast(str | SecurityPolicy, policy))
    assert_flask_csrf_strategy(policy)
    # Keep extension cookie name and policy/strategy cookie name identical.
    strategy = policy.resolve_csrf_strategy() if policy.csrf_enabled else None
    strategy_name = getattr(strategy, "cookie_name", None) if strategy is not None else None
    ext_name = getattr(ext, "csrf_cookie_name", DEFAULT_CSRF_COOKIE)
    if (
        isinstance(ext_name, str)
        and ext_name != DEFAULT_CSRF_COOKIE
        and policy.csrf is None
        and policy.csrf_cookie_name == DEFAULT_CSRF_COOKIE
    ):
        policy = replace(policy, csrf_cookie_name=ext_name)
    elif isinstance(strategy_name, str) and strategy_name:
        with contextlib.suppress(Exception):
            ext.csrf_cookie_name = strategy_name
    with contextlib.suppress(Exception):
        ext.security_policy = policy
        if isinstance(getattr(ext, "csrf_cookie_name", None), str):
            synced = policy.resolve_csrf_strategy()
            synced_name = getattr(synced, "cookie_name", None) if synced is not None else None
            if isinstance(synced_name, str) and synced_name:
                ext.csrf_cookie_name = synced_name

    app.extensions["hedron"] = extension
    app.auth_signal = ext.auth_signal  # type: ignore[attr-defined]  # Flask monkey-patch

    _apply_flask_session_cookie_defaults(app, policy)

    @app.after_request
    def _hedron_after_request(response: Response) -> Response:
        authenticated = False
        auth_fn = getattr(ext, "auth_signal", None)
        if callable(auth_fn):
            try:
                signal = auth_fn(request)
                if isinstance(signal, AuthSignal):
                    authenticated = bool(signal.authenticated)
                else:
                    authenticated = bool(getattr(signal, "authenticated", False))
            except Exception:  # noqa: BLE001
                authenticated = False
        for key, value in policy.response_headers(authenticated=authenticated).items():
            # Authenticated responses must not remain publicly cacheable even if the
            # app already set a weaker Cache-Control.
            if (authenticated and key in {"Cache-Control", "Pragma"}) or (
                key not in response.headers
            ):
                response.headers[key] = value
        seed_cookie = auto_csrf_cookie and request.method in {"GET", "HEAD"}
        if seed_cookie and policy.csrf_enabled:
            csrf_strategy = policy.resolve_csrf_strategy()
            if csrf_strategy is not None and bool(getattr(csrf_strategy, "sets_cookie", True)):
                from hedron_core.mount import cookie_path_for_mount
                from hedron_flask.csrf import (
                    csrf_cookie_force_secure,
                    csrf_cookie_should_be_secure,
                    csrf_token_for_request,
                    ensure_csrf_cookie,
                )

                cookie_name = str(
                    getattr(csrf_strategy, "cookie_name", None)
                    or getattr(ext, "csrf_cookie_name", DEFAULT_CSRF_COOKIE)
                )
                script_root = getattr(request, "script_root", "") or ""
                cookie_path = (
                    cookie_path_for_mount(script_root)
                    if isinstance(script_root, str) and script_root
                    else "/"
                )
                configured = getattr(ext, "csrf_cookie_path", None)
                if isinstance(configured, str) and configured:
                    cookie_path = configured
                force = csrf_cookie_force_secure(
                    getattr(ext, "csrf_cookie_secure", None),
                    policy,
                )
                ensure_csrf_cookie(
                    response,
                    csrf_token_for_request(
                        request,
                        cookie_name=cookie_name,
                        policy=policy,
                    ),
                    cookie_name=cookie_name,
                    secure=csrf_cookie_should_be_secure(
                        request,
                        force_secure=force,
                    ),
                    path=cookie_path,
                )
        return response
