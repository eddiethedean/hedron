"""Process-local Explorer traces, rate limits, and request guards."""

from __future__ import annotations

import logging
import time
from collections import deque
from pathlib import Path

from fastapi import HTTPException, Request, status

from hedron_core.typing_aliases import JsonObject, JsonValue

_logger = logging.getLogger("hedron.explorer")
TRACE: deque[JsonObject] = deque(maxlen=100)
RATE: dict[str, list[float]] = {}
AUDIT: deque[JsonObject] = deque(maxlen=200)
TRACE_MAXLEN = 100
AUDIT_MAXLEN = 200
RATE_LIMIT = 120
RATE_WINDOW = 60.0

# Back-compat aliases for tests importing from router.
_TRACE = TRACE
_RATE = RATE
_AUDIT = AUDIT


def redact(value: str | None) -> str | None:
    if value is None:
        return None
    if "/" in value or "\\" in value:
        return Path(value).name
    return value


def audit(event: str, **payload: JsonValue) -> None:
    AUDIT.appendleft({"event": event, **payload, "ts": time.time()})


def prune_explorer_rate(now: float) -> None:
    """Drop expired timestamps and delete idle client keys (#175)."""
    idle: list[str] = []
    for key, stamps in list(RATE.items()):
        kept = [t for t in stamps if now - t < RATE_WINDOW]
        if not kept:
            idle.append(key)
        else:
            RATE[key] = kept
    for key in idle:
        RATE.pop(key, None)


async def explorer_guards(request: Request) -> None:
    """Rate-limit and audit Explorer requests."""
    client = request.client.host if request.client else "unknown"
    now = time.time()
    prune_explorer_rate(now)
    bucket = list(RATE.get(client, []))
    if len(bucket) >= RATE_LIMIT:
        RATE[client] = bucket
        audit("rate_limited", path=str(request.url.path))
        try:
            from hedron_core.audit import SecurityAuditEventType, emit_security_audit

            emit_security_audit(
                SecurityAuditEventType.EXPLORER_DENIED,
                "Explorer rate limit exceeded",
                attributes={"path": str(request.url.path), "client": client},
            )
        except Exception as exc:  # noqa: BLE001
            _logger.debug("Security audit emit skipped during rate limit: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Explorer rate limit exceeded",
        )
    bucket.append(now)
    RATE[client] = bucket
    audit("request", path=str(request.url.path))


def reset_explorer_runtime_for_tests() -> None:
    """Clear rate-limit / audit state between tests."""
    TRACE.clear()
    RATE.clear()
    AUDIT.clear()


# Aliases matching 0.49.1 private names.
_redact = redact
_audit = audit
_prune_explorer_rate = prune_explorer_rate
