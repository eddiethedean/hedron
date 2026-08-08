"""Flask Blueprint with Hedron page/component/action registration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar

from flask import Blueprint, Flask, Response, current_app, request

from hedron_core.addressable import AddressableDescriptor
from hedron_core.component import Component
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.rendering import RenderResult
from hedron_flask.csrf import DEFAULT_CSRF_COOKIE, assert_flask_csrf_strategy, validate_csrf
from hedron_flask.responses import component_response, interaction_response

__all__ = ["HedronBlueprint", "convert_view_result", "wrap_hedron_view"]

F = TypeVar("F", bound=Callable[..., Any])

_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


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
            name = str(region).lstrip("#")
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
    if isinstance(value, InteractionResult):
        return interaction_response(
            value,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
        )
    if isinstance(value, RenderResult):
        return component_response(
            value,
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
        return component_response(
            value,  # type: ignore[arg-type]
            authenticated=authenticated,
            fragment_regions=fragment_regions,
            allow_undeclared_targets=allow_undeclared_targets,
        )
    return value


def _authenticated() -> bool:
    auth_fn = getattr(current_app, "auth_signal", None)
    if callable(auth_fn):
        signal = auth_fn(request)
        return bool(getattr(signal, "authenticated", False))
    extension = current_app.extensions.get("hedron")
    if extension is not None and hasattr(extension, "auth_signal"):
        signal = extension.auth_signal(request)
        return bool(getattr(signal, "authenticated", False))
    return False


def _csrf_settings() -> tuple[bool, str, object | None]:
    from hedron_core.security_policy import SecurityPolicy

    extension = current_app.extensions.get("hedron")
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
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        from hedron_core.security_policy import SecurityPolicy

        protect, cookie_name, policy = _csrf_settings()
        if require_csrf and protect and request.method.upper() in _UNSAFE_METHODS:
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

    return wrapped  # type: ignore[return-value]


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


def attach_hedron_to_flask(
    app: Flask,
    extension: object,
    *,
    auto_csrf_cookie: bool = True,
    security: object | None = None,
) -> None:
    """Store extension state and apply security headers (and optional CSRF cookies)."""

    import contextlib

    from hedron_core.adapter import AuthSignal
    from hedron_core.security_policy import SecurityPolicy

    policy = (
        SecurityPolicy.from_name(security)  # type: ignore[arg-type]
        if security is not None
        else getattr(extension, "security_policy", None)
    )
    if policy is None:
        policy = SecurityPolicy.from_name("standard")
    if not isinstance(policy, SecurityPolicy):
        policy = SecurityPolicy.from_name(policy)
    assert_flask_csrf_strategy(policy)
    with contextlib.suppress(Exception):
        extension.security_policy = policy  # type: ignore[attr-defined]

    app.extensions["hedron"] = extension
    app.auth_signal = extension.auth_signal  # type: ignore[attr-defined]

    @app.after_request
    def _hedron_after_request(response: Response) -> Response:  # type: ignore[no-untyped-def]
        authenticated = False
        auth_fn = getattr(extension, "auth_signal", None)
        if callable(auth_fn):
            try:
                signal = auth_fn(request)
                if isinstance(signal, AuthSignal):
                    authenticated = bool(signal.authenticated)
                else:
                    authenticated = bool(getattr(signal, "authenticated", False))
            except Exception:
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
            strategy = policy.resolve_csrf_strategy()
            if strategy is not None and bool(getattr(strategy, "sets_cookie", True)):
                from hedron_flask.csrf import (
                    csrf_cookie_should_be_secure,
                    csrf_token_for_request,
                    ensure_csrf_cookie,
                )

                cookie_name = getattr(extension, "csrf_cookie_name", DEFAULT_CSRF_COOKIE)
                script_root = getattr(request, "script_root", "") or ""
                cookie_path = script_root if isinstance(script_root, str) and script_root else "/"
                configured = getattr(extension, "csrf_cookie_path", None)
                if isinstance(configured, str) and configured:
                    cookie_path = configured
                ensure_csrf_cookie(
                    response,
                    csrf_token_for_request(
                        request,
                        cookie_name=cookie_name,  # type: ignore[arg-type]
                        policy=policy,
                    ),
                    cookie_name=cookie_name,  # type: ignore[arg-type]
                    secure=csrf_cookie_should_be_secure(
                        request,
                        force_secure=getattr(extension, "csrf_cookie_secure", None),
                    ),
                    path=cookie_path,
                )
        return response
