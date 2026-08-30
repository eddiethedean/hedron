"""Portable browser context and namespaced preference storage (phase 0.15).

``BrowserContext`` separates request-derived signals from client-reported hints.
Locale, timezone, color mode, and viewport are **spoofable** — never use them for
authentication, authorization, or security decisions.

``BrowserStorage`` holds non-secret local/session preferences only. It is not an
authentication, authorization, or server-durability boundary.
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Mapping, MutableMapping
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from hedron_core.typing_aliases import JsonValue

__all__ = [
    "BrowserContext",
    "BrowserStorage",
    "BrowserStorageUnavailable",
    "StorageQuotaExceeded",
    "ViewportHint",
    "redact_cookie_value",
]

_REDACTED = "[redacted]"


def _finite_expiry(value: object, *, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"BrowserStorage {name} must be a finite number")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ValueError(f"BrowserStorage {name} must be a finite number") from exc
    if not math.isfinite(normalized):
        raise ValueError(f"BrowserStorage {name} must be a finite number")
    return normalized


# Cookie / header names whose values are always redacted in helpers.
_SECRETISH_NAME_FRAGMENTS = frozenset(
    {
        "session",
        "token",
        "secret",
        "auth",
        "csrf",
        "password",
        "credential",
        "api_key",
        "apikey",
        "jwt",
        "sid",
    }
)

# Request headers retained in the portable subset (lower-case keys).
_HEADER_SUBSET = frozenset(
    {
        "accept",
        "accept-language",
        "user-agent",
        "referer",
        "origin",
        "host",
        "sec-fetch-dest",
        "sec-fetch-mode",
        "sec-fetch-site",
        "sec-fetch-user",
        "sec-ch-ua",
        "sec-ch-ua-mobile",
        "sec-ch-ua-platform",
        "sec-ch-prefers-color-scheme",
        "x-forwarded-for",
        "x-forwarded-proto",
        "x-real-ip",
    }
)

_EMBEDDING_HEADERS = frozenset(
    {
        "sec-fetch-dest",
        "sec-fetch-mode",
        "sec-fetch-site",
        "sec-fetch-user",
    }
)


def redact_cookie_value(name: str, value: str) -> str:
    """Return a display-safe cookie value; secret-looking names are fully redacted."""
    lowered = name.lower().replace("-", "_")
    if any(fragment in lowered for fragment in _SECRETISH_NAME_FRAGMENTS):
        return _REDACTED
    if len(value) > 8:
        return f"{value[:2]}…{value[-2:]}"
    return _REDACTED if value else value


@dataclass(frozen=True, slots=True)
class ViewportHint:
    """Client-reported viewport dimensions (spoofable)."""

    width: int | None = None
    height: int | None = None


@dataclass(frozen=True, slots=True)
class BrowserContext:
    """Typed view of request + optional client hints.

    Request-derived fields (``url``, ``cookies``, ``client_address``, ``headers``,
    ``embedding``) come from the HTTP request. Client-reported fields
    (``locale``, ``timezone``, ``color_mode``, ``viewport``) are **spoofable**
    and must not drive authz, tenancy, or cache keys that imply trust.
    """

    url: str
    cookies: Mapping[str, str] = field(default_factory=dict[str, str])
    client_address: str | None = None
    headers: Mapping[str, str] = field(default_factory=dict[str, str])
    embedding: Mapping[str, str] = field(default_factory=dict[str, str])
    # --- spoofable client-reported hints (never trust for authz) ---
    locale: str | None = None
    timezone: str | None = None
    color_mode: str | None = None
    viewport: ViewportHint | None = None

    @property
    def spoofable(self) -> Mapping[str, JsonValue]:
        """Explicit map of client-reported (spoofable) fields."""
        out: dict[str, JsonValue] = {
            "locale": self.locale,
            "timezone": self.timezone,
            "color_mode": self.color_mode,
        }
        if self.viewport is not None:
            out["viewport"] = {"width": self.viewport.width, "height": self.viewport.height}
        else:
            out["viewport"] = None
        return out

    def redacted_cookies(self) -> dict[str, str]:
        """Cookie map with secret-looking values redacted for logs/diagnostics."""
        return {name: redact_cookie_value(name, value) for name, value in self.cookies.items()}

    def is_embedded(self) -> bool:
        dest = (self.embedding.get("sec-fetch-dest") or "").lower()
        return dest in {"iframe", "embed", "object", "frame"}

    @classmethod
    def from_mapping(
        cls,
        headers: Mapping[str, str],
        *,
        url: str = "",
        client_address: str | None = None,
        cookies: Mapping[str, str] | None = None,
        locale: str | None = None,
        timezone: str | None = None,
        color_mode: str | None = None,
        viewport: ViewportHint | Mapping[str, int | None] | None = None,
    ) -> BrowserContext:
        """Build a context from a header mapping (and optional spoofable hints)."""
        normalized: dict[str, str] = {}
        for key, value in headers.items():
            lower = str(key).lower()
            if lower in _HEADER_SUBSET:
                normalized[lower] = str(value)

        embedding = {k: normalized[k] for k in _EMBEDDING_HEADERS if k in normalized}

        # Prefer explicit locale; fall back to Accept-Language primary tag (still spoofable).
        resolved_locale = locale
        if resolved_locale is None:
            accept_lang = normalized.get("accept-language")
            if accept_lang:
                resolved_locale = accept_lang.split(",")[0].strip().split(";")[0] or None

        resolved_color = color_mode
        if resolved_color is None:
            resolved_color = normalized.get("sec-ch-prefers-color-scheme")

        vp: ViewportHint | None
        if viewport is None:
            vp = None
        elif isinstance(viewport, ViewportHint):
            vp = viewport
        else:
            vp = ViewportHint(
                width=viewport.get("width"),  # type: ignore[arg-type]
                height=viewport.get("height"),  # type: ignore[arg-type]
            )

        return cls(
            url=url,
            cookies=dict(cookies or {}),
            client_address=client_address,
            headers=normalized,
            embedding=embedding,
            locale=resolved_locale,
            timezone=timezone,
            color_mode=resolved_color,
            viewport=vp,
        )


class BrowserStorageUnavailable(RuntimeError):
    """Raised when storage is marked unavailable and a mutating op is attempted."""


class StorageQuotaExceeded(RuntimeError):
    """Raised when a set would exceed entry or byte quotas."""


@dataclass
class _StorageRecord:
    value: JsonValue
    expires_at: float | None = None


class BrowserStorage:
    """Namespaced non-secret preference store with quotas and expiry.

    This is **not** authentication, authorization, or durable server state.
    Call :meth:`forbid_auth_use` only to document / fail-closed accidental auth gates.
    """

    __slots__ = (
        "namespace",
        "consent_granted",
        "unavailable",
        "max_entries",
        "max_bytes",
        "_data",
    )

    def __init__(
        self,
        namespace: object,
        *,
        consent_granted: bool = False,
        unavailable: bool = False,
        max_entries: int = 64,
        max_bytes: int = 65_536,
        initial: Mapping[str, JsonValue] | None = None,
    ) -> None:
        if not isinstance(namespace, str) or not namespace:
            raise ValueError("BrowserStorage namespace must be a non-empty string")
        raw_max_entries: Any = max_entries
        raw_max_bytes: Any = max_bytes
        if (
            isinstance(raw_max_entries, bool)
            or not isinstance(raw_max_entries, int)
            or raw_max_entries < 1
        ):
            raise ValueError("BrowserStorage max_entries must be a positive integer")
        if (
            isinstance(raw_max_bytes, bool)
            or not isinstance(raw_max_bytes, int)
            or raw_max_bytes < 1
        ):
            raise ValueError("BrowserStorage max_bytes must be a positive integer")
        self.namespace = namespace
        self.consent_granted = consent_granted
        self.unavailable = unavailable
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self._data: MutableMapping[str, _StorageRecord] = {}
        if initial:
            if len(initial) > self.max_entries:
                raise StorageQuotaExceeded(
                    f"BrowserStorage {self.namespace!r} exceeds max_entries={self.max_entries}"
                )
            for key, value in initial.items():
                self._data[str(key)] = _StorageRecord(value=deepcopy(value))
            if self._byte_size() > self.max_bytes:
                self._data.clear()
                raise StorageQuotaExceeded(
                    f"BrowserStorage namespace {self.namespace!r} "
                    f"exceeds max_bytes={self.max_bytes}"
                )

    def forbid_auth_use(self) -> None:
        """BrowserStorage must never be used for authentication or authorization.

        Calling this method always raises so accidental auth gates fail closed.
        Prefer server sessions / IdP claims for identity and access control.
        """
        raise RuntimeError("BrowserStorage must not be used for authentication or authorization")

    def _purge_expired(self, *, now: float | None = None) -> None:
        stamp = time.time() if now is None else now
        expired = [
            k
            for k, rec in self._data.items()
            if rec.expires_at is not None and rec.expires_at <= stamp
        ]
        for key in expired:
            del self._data[key]

    def _byte_size(self) -> int:
        payload = {k: rec.value for k, rec in self._data.items()}
        try:
            encoded = json.dumps(
                payload,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            ).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ValueError("BrowserStorage values must be JSON-compatible") from exc
        return len(encoded)

    @staticmethod
    def _check_schema(value: JsonValue, schema: type | Mapping[str, type] | None) -> None:
        if schema is None:
            return
        if isinstance(schema, type):
            if not isinstance(value, schema):
                raise TypeError(
                    "BrowserStorage value type "
                    f"{type(value).__name__} does not match schema {schema!r}"
                )
            return
        if not isinstance(value, Mapping):
            raise TypeError("BrowserStorage object schema requires a mapping value")
        for key, expected_type in schema.items():
            if key not in value:
                raise TypeError(f"BrowserStorage value missing required key {key!r}")
            if not isinstance(value[key], expected_type):
                actual = repr(type(value[key]))
                raise TypeError(
                    f"BrowserStorage key {key!r} expected {expected_type!r}, got {actual}"
                )

    def get(
        self,
        key: str,
        *,
        schema: type | Mapping[str, type] | None = None,
        default: JsonValue | None = None,
    ) -> JsonValue | None:
        """Return a preference value, or ``default`` when missing/expired/unavailable."""
        if self.unavailable or not self.consent_granted:
            return default
        self._purge_expired()
        record = self._data.get(key)
        if record is None:
            return default
        self._check_schema(record.value, schema)
        return deepcopy(record.value)

    def set(
        self,
        key: str,
        value: JsonValue,
        *,
        schema: type | Mapping[str, type] | None = None,
        expires_at: float | None = None,
        ttl_seconds: float | None = None,
    ) -> None:
        """Store a preference after schema and quota checks."""
        if self.unavailable:
            raise BrowserStorageUnavailable(
                f"BrowserStorage namespace {self.namespace!r} is unavailable"
            )
        if not self.consent_granted:
            raise PermissionError(
                f"BrowserStorage namespace {self.namespace!r} requires consent_granted=True"
            )
        self._check_schema(value, schema)
        self._purge_expired()
        expiry = None if expires_at is None else _finite_expiry(expires_at, name="expires_at")
        if ttl_seconds is not None:
            expiry = time.time() + _finite_expiry(ttl_seconds, name="ttl_seconds")
        if key not in self._data and len(self._data) >= self.max_entries:
            raise StorageQuotaExceeded(
                f"BrowserStorage {self.namespace!r} exceeds max_entries={self.max_entries}"
            )
        previous = self._data.get(key)
        self._data[key] = _StorageRecord(value=deepcopy(value), expires_at=expiry)
        if self._byte_size() > self.max_bytes:
            if previous is None:
                del self._data[key]
            else:
                self._data[key] = previous
            raise StorageQuotaExceeded(
                f"BrowserStorage namespace {self.namespace!r} exceeds max_bytes={self.max_bytes}"
            )

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def clear(self) -> None:
        self._data.clear()

    def keys(self) -> list[str]:
        self._purge_expired()
        return list(self._data.keys())
