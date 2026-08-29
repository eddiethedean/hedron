"""Production operations helpers: health, readiness, shutdown, logging."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import cast

from hedron_core.adapter import LifecycleResource
from hedron_core.csrf import redact_secret_like
from hedron_core.typing_aliases import JsonObject, JsonValue

__all__ = [
    "ShutdownRegistry",
    "liveness",
    "readiness",
    "redacted_log_extra",
    "validate_proxy_trust",
]

logger = logging.getLogger("hedron.ops")


def liveness() -> dict[str, str]:
    return {"status": "ok"}


def readiness(
    checks: Mapping[str, Callable[[], bool]] | None = None,
) -> tuple[int, JsonObject]:
    """Return HTTP status and body; optional deps degrade without secret leakage."""
    results: dict[str, str] = {}
    ok = True
    for name, check in (checks or {}).items():
        try:
            results[name] = "up" if check() else "down"
            if results[name] == "down":
                ok = False
        except Exception as exc:  # noqa: BLE001
            results[name] = "error"
            ok = False
            logger.warning("readiness check %s failed: %s", name, type(exc).__name__)
    body: JsonObject = cast(
        JsonObject, {"status": "ready" if ok else "degraded", "checks": results}
    )
    return (200 if ok else 503, body)


def redacted_log_extra(payload: Mapping[str, JsonValue]) -> JsonObject:
    return cast(JsonObject, redact_secret_like(dict(payload)))


def validate_proxy_trust(
    *,
    trusted_hosts: Sequence[str] | None,
    forwarded_allow_ips: Sequence[str] | None,
    fail_closed: bool = True,
) -> None:
    """Fail closed when proxy trust is enabled but empty/unsafe."""
    if not fail_closed:
        return
    if trusted_hosts is not None and len(trusted_hosts) == 0:
        raise ValueError("trusted_hosts is empty; refusing unsafe proxy configuration")
    if forwarded_allow_ips is not None and len(forwarded_allow_ips) == 0:
        raise ValueError("forwarded_allow_ips is empty; refusing unsafe proxy configuration")


@dataclass
class ShutdownRegistry:
    """Ordered graceful shutdown for lifecycle resources."""

    resources: list[LifecycleResource] = field(default_factory=list[LifecycleResource])
    _callbacks: dict[str, Callable[[], None]] = field(default_factory=dict[str, Callable[[], None]])

    def register(self, resource: LifecycleResource, callback: Callable[[], None]) -> None:
        self.resources.append(resource)
        self._callbacks[resource.name] = callback

    def shutdown(self) -> list[str]:
        ordered = sorted(self.resources, key=lambda r: r.order, reverse=True)
        ran: list[str] = []
        for resource in ordered:
            cb = self._callbacks.get(resource.name)
            if cb is None:
                continue
            cb()
            ran.append(resource.name)
        return ran
