"""Typed session-state adapter."""

from __future__ import annotations

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
        raw = request.session.get(key) if hasattr(request, "session") else None
        if raw is None:
            self._value = self._default(annotation)
        else:
            self._value = self._adapter.validate_python(raw)

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        validated = self._adapter.validate_python(new_value)
        self._value = validated
        if hasattr(self._request, "session"):
            if isinstance(validated, BaseModel):
                self._request.session[self._key] = validated.model_dump(mode="json")
            else:
                self._request.session[self._key] = validated

    def clear(self) -> None:
        self._value = self._default(self._adapter._type)  # type: ignore[attr-defined]
        if hasattr(self._request, "session"):
            self._request.session.pop(self._key, None)

    @staticmethod
    def _default(annotation: type[Any]) -> Any:
        origin = get_origin(annotation) or annotation
        if isinstance(origin, type) and issubclass(origin, BaseModel):
            return origin()
        return None


def session_state(key: str, annotation: type[T]) -> Any:
    async def dependency(request: Request) -> SessionState[T]:
        return SessionState(request, key, annotation)

    return Depends(dependency)
