"""Flask routing helpers with portable URL reversal."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar
from urllib.parse import urlsplit

from flask import Flask, current_app, request, url_for

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderResult
from hedron_flask.csrf import DEFAULT_CSRF_COOKIE, validate_csrf
from hedron_flask.responses import component_response, interaction_response

__all__ = [
    "FlaskUrlReverser",
    "hedron_route",
]

F = TypeVar("F", bound=Callable[..., Any])

_UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


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
            if not path.startswith(prefix):
                path = f"{prefix}{path}"
        if request.root_path:
            root = request.root_path.rstrip("/")
            if not path.startswith(root):
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
    **options: Any,
) -> Callable[[F], F]:
    """Register a view that may return a component, InteractionResult, or Response."""

    def decorator(view: F) -> F:
        @app.route(rule, endpoint=endpoint, methods=methods, **options)
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if csrf_protect and request.method.upper() in _UNSAFE_METHODS:
                validate_csrf(request, cookie_name=csrf_cookie_name)
            value = current_app.ensure_sync(view)(*args, **kwargs)
            authenticated = False
            auth_fn = getattr(current_app, "auth_signal", None)
            if callable(auth_fn):
                signal = auth_fn(request)
                authenticated = bool(getattr(signal, "authenticated", False))
            if isinstance(value, InteractionResult):
                return interaction_response(value, authenticated=authenticated)
            if isinstance(value, RenderResult):
                return component_response(value, authenticated=authenticated)
            if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
                return component_response(value, authenticated=authenticated)  # type: ignore[arg-type]
            return value

        return wrapped  # type: ignore[return-value]

    return decorator
