"""Typed session-state adapter."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Generic, TypeVar, get_origin

from fastapi import Depends, Request
from pydantic import BaseModel, TypeAdapter

T = TypeVar("T")

__all__ = ["SessionState", "session_state"]


class SessionState(Generic[T]):
    """Thin typed facade over the host framework session."""

    __slots__ = ("_request", "_key", "_adapter", "_value")

    def __init__(self, request: Request, key: str, annotation: type[T]) -> None:
        self._request = request
        self._key = key
        self._adapter: TypeAdapter[T] = TypeAdapter(annotation)
        raw = request.session.get(key) if self._has_session(request) else None
        if raw is None:
            self._value = self._default(annotation)
        else:
            self._value = self._adapter.validate_python(raw)

    @staticmethod
    def _has_session(request: Request) -> bool:
        # Starlette always exposes ``request.session`` as a property; accessing it
        # without SessionMiddleware raises AssertionError. Scope is the reliable gate.
        return "session" in request.scope

    @property
    def value(self) -> T:
        if self._has_session(self._request) and self._key in self._request.session:
            self._value = self._adapter.validate_python(self._request.session[self._key])
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        validated = self._adapter.validate_python(new_value)
        self._value = validated
        if not self._has_session(self._request):
            raise RuntimeError(
                "SessionState write requires SessionMiddleware "
                "(no 'session' in request scope); install SessionMiddleware "
                "or avoid persisting session state on this request."
            )
        if isinstance(validated, BaseModel):
            self._request.session[self._key] = validated.model_dump(mode="json")
        else:
            self._request.session[self._key] = validated

    def clear(self) -> None:
        self._value = self._default(self._adapter._type)  # type: ignore[attr-defined]
        if not self._has_session(self._request):
            raise RuntimeError(
                "SessionState.clear requires SessionMiddleware (no 'session' in request scope)."
            )
        self._request.session.pop(self._key, None)

    @staticmethod
    def _default(annotation: type[Any]) -> Any:
        origin = get_origin(annotation) or annotation
        if isinstance(origin, type) and issubclass(origin, BaseModel):
            return origin()
        return None


@lru_cache(maxsize=256)
def _session_dependency(key: str, annotation: type[T]) -> Any:
    async def dependency(request: Request) -> SessionState[T]:
        return SessionState(request, key, annotation)

    return dependency


def session_state(key: str, annotation: type[T]) -> Any:
    dependency = _session_dependency(key, annotation)

    return Depends(dependency)
