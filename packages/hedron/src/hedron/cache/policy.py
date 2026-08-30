"""Cache vary/reject policy for decorator-backed data and component caches."""

from __future__ import annotations

from collections.abc import Mapping

from hedron_core.cache import CacheScope

__all__ = ["htmx_vary_dimensions"]


def htmx_vary_dimensions(*, vary_on_target: bool = False) -> tuple[str, ...]:
    """Cache/response dimensions that separate pages from HTMX fragments."""
    dims = ("HX-Request", "HX-History-Restore-Request")
    if vary_on_target:
        return (*dims, "HX-Target")
    return dims


_SENSITIVE_SCOPES = frozenset(
    {
        CacheScope.PRIVATE.value,
        CacheScope.USER.value,
        CacheScope.TENANT.value,
        CacheScope.SESSION.value,
    }
)
_PUBLIC_SENSITIVE_NAMES = frozenset(
    {"user", "user_id", "request", "session", "tenant", "tenant_id"}
)


def should_reject_cache(
    *,
    scope: str,
    args: tuple[object, ...],
    kwargs: Mapping[str, object],
    vary_on: tuple[str, ...],
    bound: Mapping[str, object] | None = None,
) -> str | None:
    if scope in _SENSITIVE_SCOPES and not vary_on:
        return f"scope {scope!r} requires vary_on dimensions"
    if scope in _SENSITIVE_SCOPES and vary_on:
        source = bound if bound is not None else kwargs
        missing = [k for k in vary_on if k not in source or source[k] is None]
        if missing:
            return f"scope {scope!r} missing vary_on values: {', '.join(missing)}"
    if scope == CacheScope.PUBLIC.value:
        source = bound if bound is not None else kwargs
        if any(k in _PUBLIC_SENSITIVE_NAMES for k in source):
            return "user-specific kwargs under public scope"
        # Positional request-like objects must not be cached publicly.
        for arg in args:
            type_name = type(arg).__name__
            if type_name in {"Request", "HTTPConnection"} or "Session" in type_name:
                return "request/session positional arg under public scope"
    return None


_should_reject_cache = should_reject_cache
