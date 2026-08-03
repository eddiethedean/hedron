"""Flask routing helpers with portable URL reversal."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from flask import Flask, current_app, url_for

from hedron_core.adapter import UrlReverseRequest
from hedron_core.component import Component
from hedron_core.interaction import InteractionResult
from hedron_core.rendering import RenderResult
from hedron_flask.responses import component_response, interaction_response

__all__ = [
    "FlaskUrlReverser",
    "hedron_route",
]

F = TypeVar("F", bound=Callable[..., Any])


class FlaskUrlReverser:
    """Reverse endpoint names via Flask ``url_for``."""

    def __init__(self, app: Flask) -> None:
        self._app = app

    def reverse(self, request: UrlReverseRequest) -> str:
        with self._app.app_context():
            path = url_for(request.name, *request.args, **dict(request.kwargs))
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
    **options: Any,
) -> Callable[[F], F]:
    """Register a view that may return a component, InteractionResult, or Response."""

    def decorator(view: F) -> F:
        @app.route(rule, endpoint=endpoint, methods=methods, **options)
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            value = current_app.ensure_sync(view)(*args, **kwargs)
            if isinstance(value, InteractionResult):
                return interaction_response(value)
            if isinstance(value, RenderResult):
                return component_response(value)
            if isinstance(value, (Component, str)) or hasattr(value, "__hedron_component__"):
                return component_response(value)  # type: ignore[arg-type]
            return value

        return wrapped  # type: ignore[return-value]

    return decorator
