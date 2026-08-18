"""Flask routing helpers with portable URL reversal."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar
from urllib.parse import urlsplit

from flask import Flask, current_app, request, url_for

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.rendering import RenderResult
from hedron_flask.csrf import DEFAULT_CSRF_COOKIE, validate_csrf
from hedron_flask.responses import component_response, interaction_response

__all__ = [
    "FlaskUrlReverser",
    "hedron_route",
]

F = TypeVar("F", bound=Callable[..., Any])

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


class FlaskUrlReverser:
    """Reverse endpoint names via Flask ``url_for``."""

    def __init__(self, app: Flask) -> None:
        self._app = app

    def reverse(self, request: UrlReverseRequest) -> str:
        with self._app.app_context():
            # Force path-only so SERVER_NAME never yields absolute URLs that then
            # get prefixed into broken forms like ``/apphttp://…``.
            path = url_for(
                request.name,
                *request.args,
                _external=False,
                **dict(request.kwargs),
            )
        parsed = urlsplit(path)
        if parsed.scheme or parsed.netloc:
            path = parsed.path or "/"
            if parsed.query:
                path = f"{path}?{parsed.query}"
        if request.script_name:
            prefix = request.script_name.rstrip("/")
            if path != prefix and not path.startswith(prefix + "/"):
                path = f"{prefix}{path}"
        if request.root_path:
            root = request.root_path.rstrip("/")
            if path != root and not path.startswith(root + "/"):
                path = f"{root}{path}"
        return path


def hedron_route(
    app: Flask,
    rule: str,
    *,
    endpoint: str | None = None,
    methods: list[str] | None = None,
    csrf_protect: bool = True,
    csrf_cookie_name: str = DEFAULT_CSRF_COOKIE,
    fragment_regions: Sequence[FragmentRegion | str] | None = None,
    allow_undeclared_targets: bool = False,
    **options: Any,
) -> Callable[[F], F]:
    """Register a view that may return a component, InteractionResult, or Response."""

    def decorator(view: F) -> F:
        @app.route(rule, endpoint=endpoint, methods=methods, **options)
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            from hedron_core.security_policy import SecurityPolicy

            extension = current_app.extensions.get("hedron")
            policy = getattr(extension, "security_policy", None) if extension is not None else None
            cookie = csrf_cookie_name
            if extension is not None:
                cookie = str(getattr(extension, "csrf_cookie_name", csrf_cookie_name))
            protect = csrf_protect
            if isinstance(policy, SecurityPolicy) and not policy.csrf_enabled:
                protect = False
            if protect and request.method.upper() not in _SAFE_METHODS:
                if isinstance(policy, SecurityPolicy):
                    validate_csrf(request, cookie_name=cookie, policy=policy)
                else:
                    validate_csrf(request, cookie_name=cookie)
            value = current_app.ensure_sync(view)(*args, **kwargs)
            authenticated = False
            auth_fn = getattr(current_app, "auth_signal", None)
            if callable(auth_fn):
                signal = auth_fn(request)
                authenticated = bool(getattr(signal, "authenticated", False))
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
                return component_response(
                    value,  # type: ignore[arg-type]
                    authenticated=authenticated,
                    fragment_regions=fragment_regions,
                    allow_undeclared_targets=allow_undeclared_targets,
                )
            return value

        return wrapped  # type: ignore[return-value]

    return decorator
