"""Single compatibility seam for FastAPI/Starlette implementation details.

Only this module should know that FastAPI caches OpenAPI, invalidates its
middleware stack, and exposes middleware metadata through mutable attributes.
Keeping these accesses together makes upstream upgrades reviewable and testable.
"""

from __future__ import annotations

from typing import Any, cast

from fastapi import FastAPI
from starlette.middleware import Middleware

__all__ = [
    "append_middleware",
    "cached_openapi",
    "invalidate_middleware_stack",
    "middleware_classes",
    "remove_route",
    "set_cached_openapi",
]


def cached_openapi(app: FastAPI | None) -> dict[str, Any] | None:
    return None if app is None else app.openapi_schema


def set_cached_openapi(app: FastAPI, schema: dict[str, Any]) -> None:
    app.openapi_schema = schema


def middleware_classes(app: FastAPI) -> set[type[object]]:
    return {cast(type[object], middleware.cls) for middleware in app.user_middleware}


def append_middleware(app: FastAPI, middleware: Middleware) -> None:
    app.user_middleware.append(middleware)
    invalidate_middleware_stack(app)


def invalidate_middleware_stack(app: FastAPI) -> None:
    app.middleware_stack = None


def remove_route(app: FastAPI, index: int) -> Any:
    return app.routes.pop(index)
