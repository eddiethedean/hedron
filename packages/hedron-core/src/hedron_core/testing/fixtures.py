"""Schema-checked scenario fixtures (phase 0.15)."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any, TypeGuard, TypeVar, cast

from hedron_core.csrf import redact_secret_like
from hedron_core.typing_aliases import is_string_mapping

FixtureT = TypeVar("FixtureT")


def _is_string_tuple(value: object) -> TypeGuard[tuple[str, ...]]:
    if not isinstance(value, tuple):
        return False
    return all(isinstance(item, str) for item in cast(tuple[object, ...], value))


def _is_bool(value: object) -> TypeGuard[bool]:
    return isinstance(value, bool)


def _is_int(value: object) -> TypeGuard[int]:
    return isinstance(value, int)


def _is_bytes(value: object) -> TypeGuard[bytes]:
    return isinstance(value, bytes)


def _is_string(value: object) -> TypeGuard[str]:
    return isinstance(value, str)


__all__ = [
    "AuthPrincipal",
    "BrowserHintFixture",
    "NamedConnectionFixture",
    "OidcCallbackStub",
    "StoragePayload",
    "UploadFixture",
    "redact_secrets_for_failure",
    "validate_fixture",
]


def _require_nonempty_str(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _require_mapping(name: str, value: object) -> Mapping[str, object]:
    if not is_string_mapping(value):
        raise ValueError(f"{name} must be a mapping")
    return value


@dataclass(frozen=True, slots=True)
class AuthPrincipal:
    """Authenticated principal for scenario authorization tests."""

    subject: str
    roles: tuple[str, ...] = ()
    claims: Mapping[str, object] = field(default_factory=dict[str, object])
    session_id: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty_str("subject", self.subject)
        if not _is_string_tuple(self.roles):
            raise ValueError("roles must be a tuple[str, ...]")
        _require_mapping("claims", self.claims)
        if self.session_id is not None:
            _require_nonempty_str("session_id", self.session_id)


@dataclass(frozen=True, slots=True)
class BrowserHintFixture:
    """Spoofable browser client hints (locale/timezone/theme/embed)."""

    locale: str | None = None
    timezone: str | None = None
    theme: str | None = None
    embed: bool = False
    user_agent: str | None = None

    def __post_init__(self) -> None:
        for name in ("locale", "timezone", "theme", "user_agent"):
            value = getattr(self, name)
            if value is not None:
                _require_nonempty_str(name, value)
        if not _is_bool(self.embed):
            raise ValueError("embed must be a bool")


@dataclass(frozen=True, slots=True)
class StoragePayload:
    """Namespaced browser-storage payload for non-secret preferences."""

    namespace: str
    data: Mapping[str, object] = field(default_factory=dict[str, object])
    ttl_seconds: int | None = None

    def __post_init__(self) -> None:
        _require_nonempty_str("namespace", self.namespace)
        _require_mapping("data", self.data)
        if self.ttl_seconds is not None and (
            not _is_int(self.ttl_seconds)
            or isinstance(self.ttl_seconds, bool)
            or self.ttl_seconds < 0
        ):
            raise ValueError("ttl_seconds must be a non-negative int")


@dataclass(frozen=True, slots=True)
class UploadFixture:
    """Bounded upload bytes for form/media scenario tests."""

    filename: str
    content_type: str
    content: bytes
    field_name: str = "file"

    def __post_init__(self) -> None:
        _require_nonempty_str("filename", self.filename)
        _require_nonempty_str("content_type", self.content_type)
        _require_nonempty_str("field_name", self.field_name)
        if not _is_bytes(self.content):
            raise ValueError("content must be bytes")


@dataclass(frozen=True, slots=True)
class OidcCallbackStub:
    """OIDC callback query/state stub (secrets redacted in failures)."""

    state: str
    code: str
    nonce: str | None = None
    error: str | None = None
    error_description: str | None = None

    def __post_init__(self) -> None:
        _require_nonempty_str("state", self.state)
        if self.error is None:
            _require_nonempty_str("code", self.code)
        elif not _is_string(self.error) or not self.error.strip():
            raise ValueError("error must be a non-empty string when set")
        if self.nonce is not None:
            _require_nonempty_str("nonce", self.nonce)


@dataclass(frozen=True, slots=True)
class NamedConnectionFixture:
    """Named resource/connection registry stub.

    The ``name`` maps to an app-owned :class:`~hedron.connections.ConnectionRegistry`
    entry. Scenario tests bind fixtures with
    ``hedron.connections.bind_connection_fixture(registry, fixture)``.
    """

    name: str
    provider: str
    dsn: str | None = None
    options: Mapping[str, object] = field(default_factory=dict[str, object])

    def __post_init__(self) -> None:
        _require_nonempty_str("name", self.name)
        _require_nonempty_str("provider", self.provider)
        if self.dsn is not None:
            _require_nonempty_str("dsn", self.dsn)
        _require_mapping("options", self.options)


def validate_fixture(obj: FixtureT) -> FixtureT:
    """Re-run dataclass field checks; return ``obj`` on success."""
    if not is_dataclass(obj):
        raise TypeError(f"expected a fixture dataclass, got {type(obj)!r}")
    # Frozen dataclasses validate in __post_init__; reconstruct to re-check.
    constructor = cast(Callable[..., object], type(obj))
    constructor(**asdict(cast(Any, obj)))
    return obj


def redact_secrets_for_failure(obj: object) -> object:
    """Redact secret-bearing keys for assertion failure output."""
    keys = frozenset(
        {
            "password",
            "secret",
            "token",
            "api_key",
            "authorization",
            "cookie",
            "session",
            "code",
            "nonce",
            "dsn",
            "refresh",
            "client_secret",
        }
    )
    if is_dataclass(obj) and not isinstance(obj, type):
        return redact_secret_like(asdict(cast(Any, obj)), keys=keys)
    return redact_secret_like(obj, keys=keys)
