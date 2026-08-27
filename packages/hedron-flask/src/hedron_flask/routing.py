"""Flask routing helpers with portable URL reversal."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import wraps
from typing import Any, TypeVar, cast
from urllib.parse import urlsplit

from flask import Flask, Response, current_app, request, url_for

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component, ComponentNode, NodeLike
from hedron_core.interaction import FragmentRegion, InteractionResult
from hedron_core.interaction_067 import Outcome
from hedron_core.mount import prefix_local_path
from hedron_core.rendering import RenderResult
from hedron_flask.csrf import DEFAULT_CSRF_COOKIE, validate_csrf
from hedron_flask.responses import _outcome_response, component_response, interaction_response

__all__ = [
    "FlaskUrlReverser",
    "hedron_route",
]

F = TypeVar("F", bound=Callable[..., Any])

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _as_node_like(value: object) -> NodeLike | Component[Any]:
    if isinstance(value, Component):
        return value
    if isinstance(value, ComponentNode):
        return value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return cast(NodeLike, value)


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
            path = prefix_local_path(path, request.script_name)
        if request.root_path:
            path = prefix_local_path(path, request.root_path)
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
            if isinstance(policy, SecurityPolicy):
                protect = bool(policy.csrf_enabled)
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
            from hedron_flask.identity import expected_hedron_app_id

            try:
                value = compile_to_interaction(
                    value, expected_app_id=expected_hedron_app_id(extension)
                )
            except HedronError as exc:
                code = getattr(exc.diagnostic, "code", "")
                status = 403 if str(code).startswith("HED-UPDATE-0003") else 400
                return Response(str(exc), status=status, content_type="text/plain")
            if isinstance(value, Outcome):
                return _outcome_response(
                    value,
                    authenticated=authenticated,
                    fragment_regions=fragment_regions,
                    allow_undeclared_targets=allow_undeclared_targets,
                    app_id=expected_hedron_app_id(extension),
                )
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
            if isinstance(value, (Component, str, ComponentNode)) or hasattr(
                value, "__hedron_component__"
            ):
                return component_response(
                    _as_node_like(value),
                    authenticated=authenticated,
                    fragment_regions=fragment_regions,
                    allow_undeclared_targets=allow_undeclared_targets,
                )
            return value

        return cast(F, wrapped)

    return decorator
