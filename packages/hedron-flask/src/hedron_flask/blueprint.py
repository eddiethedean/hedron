"""Flask Blueprint with Hedron page/component/action registration."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar

from flask import Blueprint, Flask, Response, current_app, request

from hedron_core.addressable import AddressableDescriptor
from hedron_core.component import Component
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderResult
from hedron_flask.csrf import DEFAULT_CSRF_COOKIE, validate_csrf
from hedron_flask.responses import component_response, interaction_response

__all__ = ["HedronBlueprint", "convert_view_result", "wrap_hedron_view"]

F = TypeVar("F", bound=Callable[..., Any])

_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def convert_view_result(value: Any, *, authenticated: bool = False) -> Any:
    """Convert Hedron return types to Flask responses; pass through native Responses."""
    if isinstance(value, Response):
        return value
    if isinstance(value, InteractionResult):
        return interaction_response(value, authenticated=authenticated)
    if isinstance(value, RenderResult):
        return component_response(value, authenticated=authenticated)
    if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
        return component_response(value, authenticated=authenticated)  # type: ignore[arg-type]
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


def _csrf_settings() -> tuple[bool, str]:
    extension = current_app.extensions.get("hedron")
    if extension is None:
        return True, DEFAULT_CSRF_COOKIE
    return bool(getattr(extension, "csrf_protect", True)), str(
        getattr(extension, "csrf_cookie_name", DEFAULT_CSRF_COOKIE)
    )


def wrap_hedron_view(
    view: F,
    *,
    require_csrf: bool,
) -> F:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        protect, cookie_name = _csrf_settings()
        if require_csrf and protect and request.method.upper() in _UNSAFE_METHODS:
            validate_csrf(request, cookie_name=cookie_name)
        value = current_app.ensure_sync(view)(*args, **kwargs)
        return convert_view_result(value, authenticated=_authenticated())

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
        **options: Any,
    ) -> Callable[[F], F]:
        method_list = list(methods or ("GET",))
        require_csrf = any(m.upper() not in _SAFE_METHODS for m in method_list)

        def decorator(view: F) -> F:
            wrapped = wrap_hedron_view(view, require_csrf=require_csrf)
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
        **options: Any,
    ) -> Callable[[F], F]:
        method_list = list(methods or ("GET",))
        require_csrf = any(m.upper() not in _SAFE_METHODS for m in method_list)

        def decorator(view: F) -> F:
            wrapped = wrap_hedron_view(view, require_csrf=require_csrf)
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
        **options: Any,
    ) -> Callable[[F], F]:
        method_list = list(methods or ("POST",))

        def decorator(view: F) -> F:
            wrapped = wrap_hedron_view(view, require_csrf=True)
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
        **options: Any,
    ) -> None:
        """Expose an ``@addressable`` factory at ``path`` (GET by default)."""

        method_list = list(methods or ("GET",))
        require_csrf = any(m.upper() not in _SAFE_METHODS for m in method_list)
        ep = endpoint or f"hedron_{descriptor.logical_id.replace(':', '_').replace('.', '_')}"

        def view(**kwargs: Any) -> Any:
            return descriptor.factory(**kwargs)

        wrapped = wrap_hedron_view(view, require_csrf=require_csrf)
        self.add_url_rule(path, endpoint=ep, view_func=wrapped, methods=method_list, **options)


def attach_hedron_to_flask(
    app: Flask,
    extension: Any,
    *,
    auto_csrf_cookie: bool = True,
) -> None:
    """Store extension state and optionally seed CSRF cookies on safe responses."""

    app.extensions["hedron"] = extension
    app.auth_signal = extension.auth_signal  # type: ignore[attr-defined]
    if not auto_csrf_cookie:
        return

    @app.after_request
    def _attach_csrf(response: Response) -> Response:  # type: ignore[no-untyped-def]
        if request.method in {"GET", "HEAD"}:
            from hedron_flask.csrf import csrf_token_for_request, ensure_csrf_cookie

            ensure_csrf_cookie(
                response,
                csrf_token_for_request(request, cookie_name=extension.csrf_cookie_name),
                cookie_name=extension.csrf_cookie_name,
                secure=request.is_secure,
            )
        return response
