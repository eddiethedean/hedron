"""Typed secret wrapper that never appears in public representations."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Generic, TypeVar, cast, get_args, get_origin, overload

from pydantic import GetCoreSchemaHandler, TypeAdapter, ValidationError
from pydantic_core import core_schema

from hedron_core.diagnostics import error

T = TypeVar("T")

_REDACTED = "***"


def _validate_secret_inner(source_type: object, value: object) -> object:
    """Validate ``value`` against the inner type of ``Secret[T]`` when present.

    Raises:
        HedronError: When pydantic rejects the value for the annotated inner type.
    """
    args = get_args(source_type)
    if not args:
        return value
    inner = args[0]
    origin = get_origin(inner) or inner
    if origin is Any:
        return value
    try:
        return TypeAdapter(inner).validate_python(value)
    except ValidationError as exc:
        raise error(
            "HED-SEC-0010",
            title="Secret value type mismatch",
            explanation=f"Secret expected {inner!r}, got {type(value).__name__}.",
            remediation="Pass a value matching the Secret[T] type parameter.",
        ) from exc


class Secret(Generic[T]):
    """Typed sensitive value that never appears in public representations."""

    __slots__ = ("_value",)
    _value: T

    def __init__(self, value: T) -> None:
        object.__setattr__(self, "_value", value)

    def reveal(self) -> T:
        return self._value

    def __str__(self) -> str:
        return _REDACTED

    def __repr__(self) -> str:
        return "Secret(***)"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Secret):
            return NotImplemented
        other_secret = cast(Secret[object], other)
        return self.reveal() == other_secret.reveal()

    def __hash__(self) -> int:
        try:
            return hash(("Secret", self.reveal()))
        except TypeError:
            # Unhashable payloads (e.g. list) fall back to identity hashing.
            return hash(("Secret", id(self)))

    def __getstate__(self) -> dict[str, object]:
        return {"value": _REDACTED}

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Secret is immutable")

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: object,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        del handler

        def validate(value: object) -> Secret[object]:
            if isinstance(value, Secret):
                secret = cast(Secret[object], value)
                inner = _validate_secret_inner(source_type, secret.reveal())
                return Secret(inner)
            inner = _validate_secret_inner(source_type, value)
            return Secret(inner)

        return core_schema.no_info_plain_validator_function(
            validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda _v: _REDACTED,
                info_arg=False,
                return_schema=core_schema.str_schema(),
            ),
        )


def is_secret(value: object) -> bool:
    return isinstance(value, Secret)


def redact_value(value: object) -> object:
    if isinstance(value, Secret):
        return _REDACTED
    if isinstance(value, list):
        return [redact_value(item) for item in cast(list[object], value)]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in cast(tuple[object, ...], value))
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        return {key: redact_value(item) for key, item in mapping.items()}
    if isinstance(value, set):
        return {redact_value(item) for item in cast(set[object], value)}
    if isinstance(value, frozenset):
        return frozenset(redact_value(item) for item in cast(frozenset[object], value))
    return value


def _secret_like_key(key: str, secret_keys: frozenset[str]) -> bool:
    lowered = str(key).lower()
    normalized = lowered.replace("-", "_")
    if lowered in secret_keys or normalized in secret_keys:
        return True
    tokens = [part for part in re.split(r"[-_.]", lowered) if part]
    return any(token in secret_keys for token in tokens)


@overload
def redact_secret_like(
    value: Mapping[str, object], *, keys: frozenset[str] | None = None
) -> dict[str, object]: ...


@overload
def redact_secret_like(
    value: list[object], *, keys: frozenset[str] | None = None
) -> list[object]: ...


@overload
def redact_secret_like(value: object, *, keys: frozenset[str] | None = None) -> object: ...


def redact_secret_like(value: object, *, keys: frozenset[str] | None = None) -> object:
    """Redact mapping values whose keys look secret-bearing."""
    secret_keys = keys or frozenset(
        {
            "password",
            "passwd",
            "secret",
            "token",
            "api_key",
            "authorization",
            "cookie",
            "session",
        }
    )
    if isinstance(value, Secret):
        return "[redacted]"
    if isinstance(value, Mapping):
        mapping = cast(Mapping[object, object], value)
        out: dict[str, object] = {}
        for key, item in mapping.items():
            if _secret_like_key(str(key), secret_keys):
                out[str(key)] = "[redacted]"
            else:
                out[str(key)] = redact_secret_like(item, keys=secret_keys)
        return out
    if isinstance(value, list):
        items = cast(list[object], value)
        return [redact_secret_like(item, keys=secret_keys) for item in items]
    if isinstance(value, tuple):
        items = cast(tuple[object, ...], value)
        return tuple(redact_secret_like(item, keys=secret_keys) for item in items)
    if isinstance(value, set):
        items = cast(set[object], value)
        return {redact_secret_like(item, keys=secret_keys) for item in items}
    if isinstance(value, frozenset):
        items = cast(frozenset[object], value)
        return frozenset(redact_secret_like(item, keys=secret_keys) for item in items)
    return value
