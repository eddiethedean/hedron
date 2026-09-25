"""Typed access to application state attached to Starlette requests."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, cast


class AppStateLike(Protocol):
    """Structural view of Starlette's dynamic state container."""

    def __getattr__(self, name: str) -> object: ...


class AppLike(Protocol):
    """Structural view of an ASGI application with dynamic state."""

    state: AppStateLike


class _RequestWithApp(Protocol):
    app: AppLike


class _RequestWithState(Protocol):
    state: AppStateLike


class _RequestWithJson(Protocol):
    async def json(self) -> object: ...


class _RequestWithForm(Protocol):
    async def form(self) -> Mapping[str, object]: ...


class _RequestWithHeaders(Protocol):
    headers: Mapping[str, str]


class _ValidationError(Protocol):
    def errors(self) -> list[Mapping[str, object]]: ...


def request_app(request: object) -> AppLike:
    """Return a Starlette request's app without carrying its ``Any`` app type."""
    return cast(_RequestWithApp, request).app


def request_state(request: object) -> AppStateLike:
    """Return the app state associated with a Starlette request."""
    return request_app(request).state


def request_context_state(request: object) -> AppStateLike:
    """Return Starlette's per-request state container."""
    return cast(_RequestWithState, request).state


async def request_json(request: object) -> object:
    """Decode a request body without inheriting Starlette's ``Any`` return."""
    return await cast(_RequestWithJson, request).json()


async def request_form(request: object) -> Mapping[str, object]:
    """Read form fields through Starlette's object-valued mapping surface."""
    return await cast(_RequestWithForm, request).form()


def request_headers(request: object) -> Mapping[str, str]:
    """Read Starlette request headers as a string mapping."""
    return cast(_RequestWithHeaders, request).headers


def validation_errors(exc: object) -> list[Mapping[str, object]]:
    """Return framework validation errors through an object-valued typed boundary."""
    return cast(_ValidationError, exc).errors()


def state_value(state: object, name: str, default: object = None) -> object:
    """Read an optional dynamic state attribute as ``object`` rather than ``Any``."""
    from hedron_core.typing_support import dynamic_attribute

    return dynamic_attribute(state, name, default)
