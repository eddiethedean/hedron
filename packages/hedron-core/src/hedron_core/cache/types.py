"""Cache scope and event types."""

from __future__ import annotations

from dataclasses import dataclass

from hedron_core.compat import StrEnum


class CacheScope(StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    USER = "user"
    TENANT = "tenant"
    SESSION = "session"


@dataclass(frozen=True, slots=True)
class CacheEvent:
    kind: str  # hit|miss|wait|store|reject|invalidate
    key_fingerprint: str
    scope: str
    age_ms: float | None = None
    size: int | None = None
    tags: tuple[str, ...] = ()
    detail: str = ""
